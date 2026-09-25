from html import unescape

import pytest

from knockknock.jokes import JOKES
from knockknock.ratings import Rating
from knockknock.sequence import tell
from knockknock.web import create_app


class MemoryRatingStore:
    def __init__(self):
        self.ratings = []

    def save(self, rating):
        self.ratings.append(rating)


@pytest.fixture
def store():
    return MemoryRatingStore()


@pytest.fixture
def client(store):
    return create_app({"TESTING": True, "RATING_STORE": store}).test_client()


def test_random_page_uses_selected_joke_and_domain_sequence(client, monkeypatch):
    monkeypatch.setattr("knockknock.web.random.choice", lambda jokes: jokes[0])

    response = client.get("/")

    assert response.status_code == 200
    body = unescape(response.get_data(as_text=True))
    assert all(line in body for line in tell(JOKES[0]))
    assert "Another random joke" in body


def test_catalogue_contains_each_joke_once_and_links_by_id(client):
    response = client.get("/jokes")
    body = unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    for joke in JOKES:
        assert body.count(joke.name) == 1
        assert f'/jokes/{joke.id}"' in body


def test_detail_page_contains_joke_and_domain_sequence(client):
    joke = JOKES[1]

    response = client.get(f"/jokes/{joke.id}")

    assert response.status_code == 200
    body = unescape(response.get_data(as_text=True))
    assert joke.name in body
    assert all(line in body for line in tell(joke))


def test_unknown_joke_returns_404(client):
    response = client.get("/jokes/not-a-real-joke")

    assert response.status_code == 404
    assert response.data


@pytest.mark.parametrize("value", ["1", "5"])
def test_rating_is_saved_and_redirects(client, store, value):
    joke = JOKES[0]

    response = client.post(f"/jokes/{joke.id}/ratings", data={"rating": value})

    assert response.status_code == 302
    assert response.location.endswith(f"/jokes/{joke.id}")
    assert len(store.ratings) == 1
    assert store.ratings[0].joke_id == joke.id
    assert store.ratings[0].value == int(value)
    assert isinstance(store.ratings[0], Rating)


@pytest.mark.parametrize("value", [None, "", "True", "1.0", "0", "6"])
def test_invalid_rating_is_not_saved(client, store, value):
    data = {} if value is None else {"rating": value}

    response = client.post("/jokes/cow-says/ratings", data=data)

    assert response.status_code == 400
    assert "whole-number rating from 1 to 5" in response.get_data(as_text=True)
    assert store.ratings == []


def test_rating_store_oserror_is_controlled(client, monkeypatch):
    def fail(_rating):
        raise OSError("read-only")

    monkeypatch.setattr(client.application.extensions["knockknock_rating_store"], "save", fail)

    response = client.post("/jokes/cow-says/ratings", data={"rating": "3"})

    assert response.status_code == 500
    assert "could not be saved" in response.get_data(as_text=True)
