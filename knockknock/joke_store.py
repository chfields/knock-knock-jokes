"""Persistence for the web joke catalogue."""

import re
from importlib import import_module
from typing import Iterable, Optional, Protocol

from .jokes import Joke

BUILTIN_JOKE_MIGRATIONS = (
    ("2026-10-03-add-justin-harry-ice-cream", ("justin", "harry", "ice-cream")),
)


class DuplicateJokeError(Exception):
    """Raised when a joke with the same setup already exists."""


class JokeStore(Protocol):
    """Storage used by the web application for its catalogue."""

    def list(self) -> list[Joke]:
        """Return every available joke in display order."""

    def get(self, joke_id: str) -> Optional[Joke]:
        """Return a joke by ID, if it exists."""

    def create(self, name: str, punchline: str) -> Joke:
        """Persist and return a new joke."""

    def delete(self, joke_id: str) -> bool:
        """Delete a joke, returning whether one was removed."""


def _joke_id(name: str) -> str:
    """Make a URL-safe ID from a user-provided setup line."""
    joke_id = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    return joke_id or "joke"


class MemoryJokeStore:
    """In-memory catalogue for local development and tests."""

    def __init__(self, jokes: Iterable[Joke]) -> None:
        self.jokes = {joke.id: joke for joke in jokes}

    def list(self) -> list[Joke]:
        return list(self.jokes.values())

    def get(self, joke_id: str) -> Optional[Joke]:
        return self.jokes.get(joke_id)

    def create(self, name: str, punchline: str) -> Joke:
        name = name.strip()
        punchline = punchline.strip()
        if any(joke.name == name for joke in self.jokes.values()):
            raise DuplicateJokeError
        base_id = _joke_id(name)
        joke_id = base_id
        suffix = 2
        while joke_id in self.jokes:
            joke_id = "{}-{}".format(base_id, suffix)
            suffix += 1
        joke = Joke(name, punchline, joke_id)
        self.jokes[joke.id] = joke
        return joke

    def delete(self, joke_id: str) -> bool:
        return self.jokes.pop(joke_id, None) is not None


class PostgresJokeStore:
    """Persist the web catalogue in PostgreSQL."""

    def __init__(self, database_url: str, jokes: Iterable[Joke]) -> None:
        try:
            connection_pool = import_module("psycopg_pool").ConnectionPool
        except ImportError as error:
            raise RuntimeError(
                "PostgreSQL jokes require the postgres extra. "
                "Install it with: pip install 'knock-knock-jokes[postgres]'"
            ) from error
        self._pool = connection_pool(database_url, kwargs={"autocommit": True}, open=False)
        self._pool.open(wait=True)
        self._create_schema()
        self._seed(jokes)
        self._apply_builtin_joke_migrations(jokes)

    def _connect(self):
        return self._pool.connection()

    def _create_schema(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jokes (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        punchline TEXT NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS builtin_joke_migrations (
                        id TEXT PRIMARY KEY
                    )
                    """
                )

    def _seed(self, jokes: Iterable[Joke]) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT EXISTS (SELECT 1 FROM jokes)")
                if cursor.fetchone()[0]:
                    return
                for joke in jokes:
                    cursor.execute(
                        """
                        INSERT INTO jokes (id, name, punchline) VALUES (%s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (joke.id, joke.name, joke.punchline),
                    )

    def _apply_builtin_joke_migrations(self, jokes: Iterable[Joke]) -> None:
        """Apply each built-in catalogue addition to existing databases once."""
        jokes_by_id = {joke.id: joke for joke in jokes}
        with self._connect() as connection:
            with connection.transaction():
                with connection.cursor() as cursor:
                    for migration_id, joke_ids in BUILTIN_JOKE_MIGRATIONS:
                        cursor.execute(
                            """
                            INSERT INTO builtin_joke_migrations (id) VALUES (%s)
                            ON CONFLICT (id) DO NOTHING
                            RETURNING id
                            """,
                            (migration_id,),
                        )
                        if cursor.fetchone() is None:
                            continue
                        for joke_id in joke_ids:
                            joke = jokes_by_id[joke_id]
                            cursor.execute(
                                """
                                INSERT INTO jokes (id, name, punchline) VALUES (%s, %s, %s)
                                ON CONFLICT (id) DO NOTHING
                                """,
                                (joke.id, joke.name, joke.punchline),
                            )

    def list(self) -> list[Joke]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, punchline FROM jokes ORDER BY name")
                return [Joke(name, punchline, joke_id) for joke_id, name, punchline in cursor.fetchall()]

    def get(self, joke_id: str) -> Optional[Joke]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, punchline FROM jokes WHERE id = %s", (joke_id,))
                row = cursor.fetchone()
        return Joke(row[1], row[2], row[0]) if row else None

    def create(self, name: str, punchline: str) -> Joke:
        name = name.strip()
        punchline = punchline.strip()
        base_id = _joke_id(name)
        Joke(name, punchline, base_id)
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM jokes WHERE id LIKE %s", (base_id + "%",))
                existing_ids = {row[0] for row in cursor.fetchall()}
                joke_id = base_id
                suffix = 2
                while joke_id in existing_ids:
                    joke_id = "{}-{}".format(base_id, suffix)
                    suffix += 1
                try:
                    cursor.execute(
                        "INSERT INTO jokes (id, name, punchline) VALUES (%s, %s, %s)",
                        (joke_id, name, punchline),
                    )
                except Exception as error:
                    if getattr(error, "sqlstate", None) == "23505":
                        raise DuplicateJokeError from error
                    raise
        return Joke(name, punchline, joke_id)

    def delete(self, joke_id: str) -> bool:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM jokes WHERE id = %s", (joke_id,))
                return cursor.rowcount == 1

    def close(self) -> None:
        """Close the database connection pool."""
        self._pool.close()
