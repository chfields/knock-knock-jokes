import hashlib
from html import unescape

import pytest
from werkzeug.middleware.proxy_fix import ProxyFix

from knockknock.jokes import JOKES
from knockknock.ratings import DuplicateVoteError, JsonlRatingStore, Rating, RatingSummary
from knockknock.sequence import tell
from knockknock.web import _count_text, create_app


class MemoryRatingStore:
    def __init__(self):
        self.ratings = []

    def save(self, rating, voter_key=None):
        if voter_key:
            existing_rating = self.rating_for(rating.joke_id, voter_key)
            if existing_rating is not None:
                raise DuplicateVoteError(existing_rating)
        self.ratings.append((rating, voter_key))

    def summary(self, joke_id):
        values = [rating.value for rating, _ in self.ratings if rating.joke_id == joke_id]
        return RatingSummary(float(sum(values)) / len(values) if values else None, len(values))

    def summaries(self, joke_ids):
        return {joke_id: self.summary(joke_id) for joke_id in joke_ids}

    def rating_for(self, joke_id, voter_key):
        for rating, identity in self.ratings:
            if rating.joke_id == joke_id and identity == voter_key:
                return rating.value
        return None

    @property
    def saved_ratings(self):
        return [rating for rating, _ in self.ratings]


@pytest.fixture
def store():
    return MemoryRatingStore()


@pytest.fixture
def client(store):
    return create_app({"TESTING": True, "RATING_STORE": store}).test_client()


def test_create_app_selects_postgres_store_when_database_url_is_set(monkeypatch):
    database_url = "postgres://ratings.example/knockknock"
    created_with = []

    class FakePostgresRatingStore:
        def __init__(self, url):
            created_with.append(url)

    monkeypatch.setattr("knockknock.web.PostgresRatingStore", FakePostgresRatingStore)

    app = create_app({"DATABASE_URL": database_url})

    assert isinstance(app.extensions["knockknock_rating_store"], FakePostgresRatingStore)
    assert created_with == [database_url]


def test_create_app_uses_jsonl_store_when_database_url_is_unset(tmp_path):
    rating_path = tmp_path / "ratings.jsonl"

    app = create_app({"DATABASE_URL": None, "RATING_STORE_PATH": rating_path})

    store = app.extensions["knockknock_rating_store"]
    assert isinstance(store, JsonlRatingStore)
    assert store.path == rating_path


def test_create_app_does_not_trust_forwarded_addresses_by_default(store, monkeypatch):
    monkeypatch.delenv("KNOCKKNOCK_TRUSTED_PROXIES", raising=False)
    app = create_app({"TESTING": True, "RATING_STORE": store})
    client = app.test_client()

    response = client.post(
        "/jokes/cow-says/ratings",
        data={"rating": "5"},
        environ_overrides={"REMOTE_ADDR": "192.0.2.2"},
        headers={"X-Forwarded-For": "198.51.100.10, 192.0.2.1"},
    )

    assert not isinstance(app.wsgi_app, ProxyFix)
    assert response.status_code == 302
    assert store.ratings[0][1] == "ip:" + hashlib.sha256(b"192.0.2.2").hexdigest()


def test_create_app_uses_trusted_proxy_count_for_forwarded_addresses(store, monkeypatch):
    monkeypatch.setenv("KNOCKKNOCK_TRUSTED_PROXIES", "2")
    app = create_app({"TESTING": True, "RATING_STORE": store})
    client = app.test_client()

    response = client.post(
        "/jokes/cow-says/ratings",
        data={"rating": "5"},
        environ_overrides={"REMOTE_ADDR": "192.0.2.2"},
        headers={"X-Forwarded-For": "198.51.100.10, 192.0.2.1"},
    )

    assert isinstance(app.wsgi_app, ProxyFix)
    assert response.status_code == 302
    assert store.ratings[0][1] == "ip:" + hashlib.sha256(b"198.51.100.10").hexdigest()


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


def test_detail_page_uses_sequence_lines_for_reveal_buttons_and_rating_form(client):
    joke = JOKES[1]
    lines = tell(joke)

    response = client.get(f"/jokes/{joke.id}")
    body = unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    assert body.index(lines[0]) < body.index(lines[1]) < body.index(lines[2])
    assert body.index(lines[2]) < body.index(lines[3]) < body.index(lines[4])
    assert '<button id="reveal-setup" type="button">' + lines[1] + "</button>" in body
    assert '<button id="reveal-punchline" type="button">' + lines[3] + "</button>" in body
    assert "setupButton.replaceWith(document.createTextNode(setupButton.textContent))" in body
    assert "punchlineButton.replaceWith(document.createTextNode(punchlineButton.textContent))" in body
    assert '<form method="post"' in body or '<form data-hidden method="post"' in body
    assert 'aria-label="1 star" name="rating" type="submit" value="1">★</button>' in body
    assert 'aria-label="5 stars" name="rating" type="submit" value="5">★</button>' in body
    assert "Submit rating" not in body


def test_random_page_reveals_link_with_rating_form(client, monkeypatch):
    monkeypatch.setattr("knockknock.web.random.choice", lambda jokes: jokes[0])

    response = client.get("/")
    body = unescape(response.get_data(as_text=True))

    assert response.status_code == 200
    assert '<p data-hidden data-reveal-step="random-joke">' in body
    assert "const randomJokeLink = document.querySelector('[data-reveal-step=\"random-joke\"]');" in body
    assert "reveal(randomJokeLink);" in body


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
    assert store.saved_ratings[0].joke_id == joke.id
    assert store.saved_ratings[0].value == int(value)
    assert isinstance(store.saved_ratings[0], Rating)

    redirected = client.get(response.location)
    body = unescape(redirected.get_data(as_text=True))
    assert all(line in body for line in tell(joke))
    assert "Thanks for rating this joke!" in body


@pytest.mark.parametrize("value", [None, "", "True", "1.0", "0", "6"])
def test_invalid_rating_is_not_saved(client, store, value):
    data = {} if value is None else {"rating": value}

    response = client.post("/jokes/cow-says/ratings", data=data)

    assert response.status_code == 400
    assert "whole-number rating from 1 to 5" in response.get_data(as_text=True)
    assert store.ratings == []


def test_rating_store_oserror_is_controlled(client, monkeypatch):
    def fail(_rating, _voter_key):
        raise OSError("read-only")

    monkeypatch.setattr(client.application.extensions["knockknock_rating_store"], "save", fail)

    response = client.post("/jokes/cow-says/ratings", data={"rating": "3"})

    assert response.status_code == 500
    assert "could not be saved" in response.get_data(as_text=True)


def test_repeat_html_rating_is_refused(client):
    visit = client.get("/jokes/cow-says")
    first = client.post("/jokes/cow-says/ratings", data={"rating": "5"})
    second = client.post("/jokes/cow-says/ratings", data={"rating": "3"})

    assert first.status_code == 302
    assert "HttpOnly" in visit.headers["Set-Cookie"]
    assert second.status_code == 409
    body = unescape(second.get_data(as_text=True))
    assert "You have already rated this joke." in body
    assert "You rated this joke 5 stars." in body


def test_api_catalogue_is_ordered_and_contains_ids_and_names(client):
    response = client.get("/api/jokes")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": joke.id, "name": joke.name, "averageRating": None, "ratingCount": 0} for joke in JOKES
    ]


@pytest.mark.parametrize("path", ["/api/jokes", "/jokes"])
def test_catalogues_use_one_batched_summary_call(client, store, monkeypatch, path):
    calls = []
    original_summaries = store.summaries

    def record_summaries(joke_ids):
        joke_ids = list(joke_ids)
        calls.append(joke_ids)
        return original_summaries(joke_ids)

    monkeypatch.setattr(store, "summaries", record_summaries)

    response = client.get(path)

    assert response.status_code == 200
    assert calls == [[joke.id for joke in JOKES]]


def test_api_joke_count_matches_catalogue(client):
    response = client.get("/api/jokes/count")

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.get_json() == {"count": 34, "count_label": "34"}


@pytest.mark.parametrize(
    ("count", "expected"),
    [(-1, "-1"), (0, "zero"), (1, "one"), (5, "five"), (9, "nine"), (10, "10"), (33, "33")],
)
def test_count_text(count, expected):
    assert _count_text(count) == expected


def test_api_detail_contains_tell_lines(client):
    joke = JOKES[1]
    detail = client.get(f"/api/jokes/{joke.id}")
    assert detail.status_code == 200
    assert detail.get_json() == {
        "id": joke.id, "name": joke.name, "lines": tell(joke), "averageRating": None,
        "ratingCount": 0, "myRating": None,
    }


def test_api_random_joke_returns_selected_joke_data(client, monkeypatch):
    selector = 1
    joke = JOKES[selector]
    monkeypatch.setattr("knockknock.web.random.choice", lambda selectors: selector)

    random_response = client.get("/api/jokes/random")
    assert random_response.status_code == 200
    assert random_response.get_json() == {
        "id": joke.id, "name": joke.name, "lines": tell(joke), "averageRating": None,
        "ratingCount": 0, "myRating": None,
    }


def test_api_unknown_joke_returns_404(client):
    response = client.get("/api/jokes/not-a-real-joke")
    assert response.status_code == 404


@pytest.mark.parametrize("value", [None, "", True, 0, 6, 1.0])
def test_api_invalid_rating_is_not_saved(client, store, value):
    payload = {} if value is None else {"rating": value}
    response = client.post("/api/jokes/cow-says/ratings", json=payload)
    assert response.status_code == 400
    assert "whole-number rating from 1 to 5" in response.get_json()["message"]
    assert store.ratings == []


def test_api_rating_is_saved(client, store):
    response = client.post("/api/jokes/cow-says/ratings", json={"rating": 5})
    assert response.status_code == 201
    assert response.get_json()["message"]
    assert store.saved_ratings[0].joke_id == "cow-says"
    assert store.saved_ratings[0].value == 5


def test_api_rating_store_failure_is_controlled(client, monkeypatch):
    def fail(_rating, _voter_key):
        raise OSError("read-only")

    monkeypatch.setattr(client.application.extensions["knockknock_rating_store"], "save", fail)
    response = client.post("/api/jokes/cow-says/ratings", json={"rating": 3})
    assert response.status_code == 500
    assert "could not be saved" in response.get_json()["message"]


def test_api_repeat_rating_is_refused_and_cookie_is_set(client):
    visit = client.get("/api/jokes/cow-says")
    first = client.post("/api/jokes/cow-says/ratings", json={"rating": 5})
    second = client.post("/api/jokes/cow-says/ratings", json={"rating": 3})

    assert first.status_code == 201
    assert "HttpOnly" in visit.headers["Set-Cookie"]
    assert "Max-Age=31536000" in visit.headers["Set-Cookie"]
    assert "SameSite=Lax" in visit.headers["Set-Cookie"]
    assert second.status_code == 409
    assert second.get_json() == {"message": "You have already rated this joke.", "rating": 5}


def test_api_repeat_rating_uses_the_rating_from_the_save_error(client, store, monkeypatch):
    def fail(_rating, _voter_key):
        raise DuplicateVoteError(4)

    monkeypatch.setattr(store, "save", fail)
    monkeypatch.setattr(store, "rating_for", lambda *_args: pytest.fail("rating_for should not be called"))

    response = client.post("/api/jokes/cow-says/ratings", json={"rating": 3})

    assert response.status_code == 409
    assert response.get_json()["rating"] == 4


def test_api_repeat_rating_without_cookie_uses_ip(client):
    first = client.post(
        "/api/jokes/cow-says/ratings", json={"rating": 5}, environ_overrides={"REMOTE_ADDR": "10.0.0.1"}
    )
    client.delete_cookie("knockknock_voter")
    second = client.post(
        "/api/jokes/cow-says/ratings", json={"rating": 3}, environ_overrides={"REMOTE_ADDR": "10.0.0.1"}
    )

    assert first.status_code == 201
    assert second.status_code == 409
