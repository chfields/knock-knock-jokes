"""Integration tests for PostgreSQL ratings storage."""

import os
import uuid

import pytest

from knockknock.ratings import DuplicateVoteError, PostgresRatingStore, Rating


@pytest.fixture
def postgres_store():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set")
    store = PostgresRatingStore(database_url)
    prefix = "pytest-" + uuid.uuid4().hex
    yield store, prefix
    if not store._pool.closed:
        with store._connect() as connection, connection.cursor() as cursor:
            cursor.execute("DELETE FROM joke_ratings WHERE joke_id LIKE %s", (prefix + "%",))
        store.close()


def test_postgres_store_saves_averages_and_counts(postgres_store):
    store, prefix = postgres_store
    joke_id = prefix + "-joke"

    store.save(Rating.now(joke_id, 3), "cookie:first")
    store.save(Rating.now(joke_id, 5), "cookie:second")

    assert store.summary(joke_id).average == 4.0
    assert store.summary(joke_id).count == 2
    assert store.rating_for(joke_id, "cookie:first") == 3


def test_postgres_store_summaries_returns_ratings_for_multiple_jokes(postgres_store):
    store, prefix = postgres_store
    first_joke = prefix + "-first"
    second_joke = prefix + "-second"
    unrated_joke = prefix + "-unrated"

    store.save(Rating.now(first_joke, 2), "cookie:first")
    store.save(Rating.now(first_joke, 4), "cookie:second")
    store.save(Rating.now(second_joke, 5), "cookie:first")

    summaries = store.summaries([first_joke, second_joke, unrated_joke])

    assert summaries[first_joke].average == 3.0
    assert summaries[first_joke].count == 2
    assert summaries[second_joke].average == 5.0
    assert summaries[second_joke].count == 1
    assert summaries[unrated_joke].average is None
    assert summaries[unrated_joke].count == 0


def test_postgres_store_refuses_duplicate_cookie_and_ip_votes(postgres_store):
    store, prefix = postgres_store
    cookie_joke = prefix + "-cookie"
    ip_joke = prefix + "-ip"

    store.save(Rating.now(cookie_joke, 4), "cookie:visitor")
    store.save(Rating.now(ip_joke, 2), "ip:hashed-address")

    with pytest.raises(DuplicateVoteError):
        store.save(Rating.now(cookie_joke, 5), "cookie:visitor")
    with pytest.raises(DuplicateVoteError):
        store.save(Rating.now(ip_joke, 5), "ip:hashed-address")


def test_postgres_duplicate_vote_uses_the_insert_query_result(postgres_store, monkeypatch):
    store, prefix = postgres_store
    joke_id = prefix + "-joke"
    voter_key = "cookie:visitor"
    store.save(Rating.now(joke_id, 4), voter_key)
    monkeypatch.setattr(store, "rating_for", lambda *_args: pytest.fail("rating_for should not be called"))

    with pytest.raises(DuplicateVoteError) as error:
        store.save(Rating.now(joke_id, 5), voter_key)

    assert error.value.rating == 4


def test_postgres_store_closes_its_connection_pool(postgres_store):
    store, _ = postgres_store

    store.close()

    assert store._pool.closed
