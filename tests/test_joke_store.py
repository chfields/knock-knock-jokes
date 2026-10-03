from knockknock.joke_store import PostgresJokeStore
from knockknock.jokes import Joke


class SeedCursor:
    def __init__(self):
        self.executed = []
        self._result = None

    def execute(self, query, parameters=None):
        self.executed.append((" ".join(query.split()), parameters))
        if query.startswith("SELECT EXISTS"):
            self._result = (False,)

    def fetchone(self):
        return self._result

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class SeedConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor

    def cursor(self):
        return self.cursor_instance

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class SeedStore:
    def __init__(self):
        self.cursor = SeedCursor()

    def _connect(self):
        return SeedConnection(self.cursor)


def test_legacy_catalogue_receives_new_seed_version_without_restoring_deleted_jokes():
    store = SeedStore()
    legacy_joke = Joke("Deleted", "This should not return.")
    new_joke = Joke("New", "This should appear.", "new", 2)

    PostgresJokeStore._seed(store, [legacy_joke, new_joke], existing_catalogue=True)

    inserted_jokes = [parameters for query, parameters in store.cursor.executed if "INSERT INTO jokes" in query]
    seeded_versions = [
        parameters
        for query, parameters in store.cursor.executed
        if "seed_versions" in query and "INSERT" in query
    ]
    assert inserted_jokes == [("new", "New", "This should appear.")]
    assert seeded_versions == [(1,), (2,)]


def test_new_catalogue_receives_every_seed_version():
    store = SeedStore()
    first_joke = Joke("First", "First punchline.")
    second_joke = Joke("Second", "Second punchline.", "second", 2)

    PostgresJokeStore._seed(store, (joke for joke in [first_joke, second_joke]), existing_catalogue=False)

    inserted_jokes = [parameters for query, parameters in store.cursor.executed if "INSERT INTO jokes" in query]
    assert inserted_jokes == [
        ("first", "First", "First punchline."),
        ("second", "Second", "Second punchline."),
    ]
