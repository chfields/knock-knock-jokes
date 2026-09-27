"""Rating validation and storage backends."""

import json
import logging
import os
import stat
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, Protocol, Union

import psycopg
from psycopg.errors import UniqueViolation

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Rating:
    """A validated rating for one joke."""

    joke_id: str
    value: int
    timestamp: str

    def __post_init__(self) -> None:
        if not isinstance(self.joke_id, str) or not self.joke_id.strip():
            raise ValueError("Joke ID must be a non-empty string")
        if isinstance(self.value, bool) or not isinstance(self.value, int) or not 1 <= self.value <= 5:
            raise ValueError("Rating must be an integer from 1 to 5")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValueError("Rating timestamp must be a non-empty string")

    @classmethod
    def now(cls, joke_id: str, value: int) -> "Rating":
        return cls(joke_id, value, datetime.now(timezone.utc).isoformat())


def average_rating(ratings: Iterable[Rating], joke_id: str) -> Optional[float]:
    """Return the average rating for a joke, or None if it has no ratings."""
    matching_values = [rating.value for rating in ratings if rating.joke_id == joke_id]
    if not matching_values:
        return None
    return float(sum(matching_values)) / len(matching_values)


def rating_count(ratings: Iterable[Rating], joke_id: str) -> int:
    """Return the number of ratings for a joke."""
    return sum(1 for rating in ratings if rating.joke_id == joke_id)


class RatingStore(Protocol):
    def save(self, rating: Rating, voter_key: Optional[str] = None) -> None:
        """Persist one rating."""

    def summary(self, joke_id: str) -> "RatingSummary":
        """Return the aggregate rating for a joke."""

    def rating_for(self, joke_id: str, voter_key: Optional[str]) -> Optional[int]:
        """Return a voter's rating for a joke, if it exists."""


@dataclass(frozen=True)
class RatingSummary:
    """The aggregate rating data displayed in the catalogue."""

    average: Optional[float]
    count: int


class DuplicateVoteError(Exception):
    """Raised when a visitor attempts to rate a joke more than once."""


class JsonlRatingStore:
    """Persist ratings as one JSON object per line."""

    def __init__(self, path: Union[Path, str]) -> None:
        self.path = Path(path)

    def save(self, rating: Rating, voter_key: Optional[str] = None) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not self.path.stat().st_mode & (
            stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        ):
            LOGGER.warning("Rating store %s is missing write permission", self.path)
        with self.path.open("a", encoding="utf-8") as stream:
            payload = asdict(rating)
            if voter_key is not None:
                if self.rating_for(rating.joke_id, voter_key) is not None:
                    raise DuplicateVoteError("This visitor has already rated this joke.")
                payload["voter_key"] = voter_key
            stream.write(json.dumps(payload, sort_keys=True) + "\n")

    def _ratings(self) -> Iterable[dict[str, object]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]

    def summary(self, joke_id: str) -> RatingSummary:
        ratings = self._ratings()
        values = [entry["value"] for entry in ratings if entry.get("joke_id") == joke_id]
        if not values:
            return RatingSummary(None, 0)
        return RatingSummary(float(sum(values)) / len(values), len(values))

    def rating_for(self, joke_id: str, voter_key: Optional[str]) -> Optional[int]:
        if voter_key is None:
            return None
        for entry in self._ratings():
            if entry.get("joke_id") == joke_id and entry.get("voter_key") == voter_key:
                return int(entry["value"])
        return None


class PostgresRatingStore:
    """Persist ratings in PostgreSQL with one vote per joke and visitor."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL is required for PostgresRatingStore")
        self._create_schema()

    def _connect(self):
        return psycopg.connect(self.database_url)

    def _create_schema(self) -> None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS joke_ratings (
                    id BIGSERIAL PRIMARY KEY,
                    joke_id TEXT NOT NULL,
                    value SMALLINT NOT NULL CHECK (value BETWEEN 1 AND 5),
                    rated_at TIMESTAMPTZ NOT NULL,
                    voter_key TEXT,
                    UNIQUE (joke_id, voter_key)
                )
                """
            )

    def save(self, rating: Rating, voter_key: Optional[str] = None) -> None:
        try:
            with self._connect() as connection, connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO joke_ratings (joke_id, value, rated_at, voter_key) VALUES (%s, %s, %s, %s)",
                    (rating.joke_id, rating.value, rating.timestamp, voter_key),
                )
        except UniqueViolation as error:
            raise DuplicateVoteError("This visitor has already rated this joke.") from error

    def summary(self, joke_id: str) -> RatingSummary:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT AVG(value), COUNT(*) FROM joke_ratings WHERE joke_id = %s", (joke_id,))
            average, count = cursor.fetchone()
        return RatingSummary(float(average) if average is not None else None, count)

    def rating_for(self, joke_id: str, voter_key: Optional[str]) -> Optional[int]:
        if voter_key is None:
            return None
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "SELECT value FROM joke_ratings WHERE joke_id = %s AND voter_key = %s",
                (joke_id, voter_key),
            )
            row = cursor.fetchone()
        return row[0] if row is not None else None
