"""Optional Flask web front end for the joke catalogue."""

import hashlib
import os
import random
import secrets
from pathlib import Path
from typing import Mapping, Optional

from flask import (
    Flask,
    abort,
    current_app,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from itsdangerous import BadData, URLSafeSerializer
from werkzeug.middleware.proxy_fix import ProxyFix

from .joke_store import DuplicateJokeError, JokeStore, MemoryJokeStore, PostgresJokeStore
from .jokes import JOKES, Joke
from .ratings import (
    DuplicateVoteError,
    JsonlRatingStore,
    PostgresRatingStore,
    Rating,
    RatingStore,
    RatingSummary,
)
from .sequence import tell


def _count_text(count: int) -> str:
    number_words = (
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    )
    if 0 <= count <= 9:
        return number_words[count]
    return str(count)


VOTER_COOKIE = "knockknock_voter"
VOTER_COOKIE_SALT = "knockknock-voter"


def _voter_serializer() -> URLSafeSerializer:
    """Return the serializer used for the voter-identity cookie."""
    return URLSafeSerializer(current_app.secret_key, salt=VOTER_COOKIE_SALT)


def _voter_id() -> str:
    """Return a verified voter identity, creating one when needed."""
    voter_id = getattr(g, "voter_id", None)
    if voter_id is not None:
        return voter_id

    signed_voter_id = request.cookies.get(VOTER_COOKIE)
    if signed_voter_id:
        try:
            voter_id = _voter_serializer().loads(signed_voter_id)
        except BadData:
            voter_id = None
        if isinstance(voter_id, str) and voter_id:
            g.voter_id = voter_id
            return voter_id

    voter_id = secrets.token_urlsafe(32)
    g.voter_id = voter_id
    g.set_voter_cookie = True
    return voter_id


def _voter_key() -> str:
    """Return the verified cookie identity, or a non-reversible client IP hash."""
    signed_voter_id = request.cookies.get(VOTER_COOKIE)
    if signed_voter_id:
        try:
            voter_id = _voter_serializer().loads(signed_voter_id)
        except BadData:
            voter_id = None
        if isinstance(voter_id, str) and voter_id:
            return "cookie:" + voter_id
    address = request.remote_addr or "unknown"
    return "ip:" + hashlib.sha256(address.encode("utf-8")).hexdigest()


def create_app(config: Optional[Mapping[str, object]] = None) -> Flask:
    """Create a web application with an optional injected rating store."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("KNOCKKNOCK_SECRET_KEY", "knockknock-local-web"),
        RATING_STORE_PATH=Path.home() / ".local" / "share" / "knockknock" / "ratings.jsonl",
        DATABASE_URL=os.environ.get("DATABASE_URL"),
        JOKE_STORE=None,
        TRUSTED_PROXY_COUNT=int(os.environ.get("KNOCKKNOCK_TRUSTED_PROXIES", "0")),
    )
    if config is not None:
        app.config.from_mapping(config)

    trusted_proxy_count = app.config["TRUSTED_PROXY_COUNT"]
    if trusted_proxy_count > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=trusted_proxy_count, x_proto=trusted_proxy_count)

    configured_store = app.config.get("RATING_STORE")
    if configured_store is None:
        database_url = app.config.get("DATABASE_URL")
        configured_store = (
            PostgresRatingStore(database_url)
            if isinstance(database_url, str) and database_url
            else JsonlRatingStore(app.config["RATING_STORE_PATH"])
        )
    app.extensions["knockknock_rating_store"] = configured_store

    configured_joke_store = app.config.get("JOKE_STORE")
    if configured_joke_store is None:
        database_url = app.config.get("DATABASE_URL")
        configured_joke_store = (
            PostgresJokeStore(database_url, JOKES)
            if isinstance(database_url, str) and database_url
            else MemoryJokeStore(JOKES)
        )
    app.extensions["knockknock_joke_store"] = configured_joke_store

    @app.after_request
    def set_voter_cookie(response):
        voter_id = _voter_id()
        if getattr(g, "set_voter_cookie", False):
            response.set_cookie(
                VOTER_COOKIE,
                _voter_serializer().dumps(voter_id),
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite="Lax",
                secure=request.is_secure,
            )
        return response

    def store() -> RatingStore:
        return app.extensions["knockknock_rating_store"]

    def joke_store() -> JokeStore:
        return app.extensions["knockknock_joke_store"]

    def jokes() -> list[Joke]:
        return joke_store().list()

    def joke_by_id(joke_id: str) -> Joke:
        joke = joke_store().get(joke_id)
        if joke is None:
            abort(404)
        return joke

    def joke_json(joke: Joke, summary: Optional[RatingSummary] = None) -> dict[str, object]:
        if summary is None:
            summary = store().summary(joke.id)
        return {
            "id": joke.id,
            "name": joke.name,
            "averageRating": summary.average,
            "ratingCount": summary.count,
        }

    @app.get("/api/jokes")
    def api_jokes():
        catalogue = jokes()
        summaries = store().summaries(joke.id for joke in catalogue)
        return jsonify([joke_json(joke, summaries[joke.id]) for joke in catalogue])

    @app.post("/api/jokes")
    def api_create_joke():
        payload = request.get_json(silent=True)
        name = payload.get("name") if isinstance(payload, dict) else None
        punchline = payload.get("punchline") if isinstance(payload, dict) else None
        try:
            if not isinstance(name, str) or not isinstance(punchline, str):
                raise ValueError
            joke = joke_store().create(name, punchline)
        except ValueError:
            return jsonify({"message": "Enter a setup line and a punchline."}), 400
        except DuplicateJokeError:
            return jsonify({"message": "That joke already exists."}), 409
        except OSError:
            return jsonify({"message": "Your joke could not be saved. Please try again later."}), 500
        return jsonify({**joke_json(joke), "lines": tell(joke)}), 201

    @app.get("/api/jokes/count")
    def api_joke_count():
        count = len(jokes())
        return jsonify({"count": count, "count_label": _count_text(count)})

    @app.get("/api/jokes/random")
    def api_random_joke():
        catalogue = jokes()
        if not catalogue:
            abort(404)
        joke = catalogue[random.choice(range(len(catalogue)))]
        return jsonify({**joke_json(joke), "lines": tell(joke), "myRating": store().rating_for(joke.id, _voter_key())})

    @app.get("/api/jokes/<joke_id>")
    def api_joke_detail(joke_id: str):
        joke = joke_by_id(joke_id)
        return jsonify({**joke_json(joke), "lines": tell(joke), "myRating": store().rating_for(joke.id, _voter_key())})

    @app.delete("/api/jokes/<joke_id>")
    def api_delete_joke(joke_id: str):
        if not joke_store().delete(joke_id):
            abort(404)
        return "", 204

    @app.post("/api/jokes/<joke_id>/ratings")
    def api_rate_joke(joke_id: str):
        joke = joke_by_id(joke_id)
        payload = request.get_json(silent=True)
        submitted_value = payload.get("rating") if isinstance(payload, dict) else None
        try:
            rating = Rating.now(joke.id, submitted_value)
        except (TypeError, ValueError):
            return jsonify({"message": "Please choose a whole-number rating from 1 to 5."}), 400
        try:
            store().save(rating, _voter_key())
        except DuplicateVoteError as error:
            return jsonify({"message": "You have already rated this joke.", "rating": error.rating}), 409
        except OSError:
            return jsonify({"message": "Your rating could not be saved. Please try again later."}), 500
        return jsonify({"message": "Thanks for rating this joke!", "rating": rating.value}), 201

    static_root = Path(app.root_path).parent / "web" / "dist"

    def built_app_available() -> bool:
        return (static_root / "index.html").is_file()

    @app.get("/assets/<path:filename>")
    def built_asset(filename: str):
        if not built_app_available():
            abort(404)
        return send_from_directory(static_root / "assets", filename)

    @app.get("/jokes")
    def catalogue():
        if built_app_available():
            return send_from_directory(static_root, "index.html")
        catalogue = jokes()
        summaries = store().summaries(joke.id for joke in catalogue)
        return render_template("catalogue.html", jokes=[(joke, summaries[joke.id]) for joke in catalogue])

    @app.get("/")
    def random_joke():
        if built_app_available():
            return send_from_directory(static_root, "index.html")
        catalogue = jokes()
        if not catalogue:
            abort(404)
        joke = catalogue[random.choice(range(len(catalogue)))]
        return render_template(
            "joke.html",
            joke=joke,
            lines=tell(joke),
            random_page=True,
            voter_rating=store().rating_for(joke.id, _voter_key()),
        )

    @app.get("/jokes/<joke_id>")
    def joke_detail(joke_id: str):
        joke = joke_by_id(joke_id)
        if built_app_available():
            return send_from_directory(static_root, "index.html")
        return render_template(
            "joke.html",
            joke=joke,
            lines=tell(joke),
            reveal_full=session.pop("reveal_full_joke", None) == joke.id,
            voter_rating=store().rating_for(joke.id, _voter_key()),
        )

    @app.post("/jokes/<joke_id>/ratings")
    def rate_joke(joke_id: str):
        joke = joke_by_id(joke_id)
        submitted_value = request.form.get("rating")
        try:
            if submitted_value is None:
                raise ValueError("Rating is required.")
            rating = Rating.now(joke.id, int(submitted_value))
        except (TypeError, ValueError):
            return render_template(
                "joke.html",
                joke=joke,
                lines=tell(joke),
                rating_error="Please choose a whole-number rating from 1 to 5.",
                reveal_full=True,
            ), 400
        try:
            store().save(rating, _voter_key())
        except DuplicateVoteError as error:
            return render_template(
                "joke.html",
                joke=joke,
                lines=tell(joke),
                rating_error="You have already rated this joke.",
                voter_rating=error.rating,
                reveal_full=True,
            ), 409
        except OSError:
            return render_template(
                "joke.html",
                joke=joke,
                lines=tell(joke),
                rating_error="Your rating could not be saved. Please try again later.",
                reveal_full=True,
            ), 500
        flash("Thanks for rating this joke!")
        session["reveal_full_joke"] = joke.id
        return redirect(url_for("joke_detail", joke_id=joke.id))

    return app
