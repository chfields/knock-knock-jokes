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
    with store._connect() as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM joke_ratings WHERE joke_id LIKE %s", (prefix + "%",))


def test_postgres_store_saves_averages_and_counts(postgres_store):
    store, prefix = postgres_store
    joke_id = prefix + "-joke"

    store.save(Rating.now(joke_id, 3), "cookie:first")
    store.save(Rating.now(joke_id, 5), "cookie:second")

    assert store.summary(joke_id).average == 4.0
    assert store.summary(joke_id).count == 2
    assert store.rating_for(joke_id, "cookie:first") == 3


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
