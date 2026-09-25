"""Optional Flask web front end for the joke catalogue."""

import random
from pathlib import Path
from typing import Mapping, Optional

from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from .jokes import JOKES, Joke
from .ratings import JsonlRatingStore, Rating
from .sequence import tell


def _joke_by_id(joke_id: str) -> Joke:
    for joke in JOKES:
        if joke.id == joke_id:
            return joke
    abort(404)


def create_app(config: Optional[Mapping[str, object]] = None) -> Flask:
    """Create a web application with an optional injected rating store."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="knockknock-local-web",
        RATING_STORE_PATH=Path.home() / ".local" / "share" / "knockknock" / "ratings.jsonl",
    )
    if config is not None:
        app.config.from_mapping(config)

    configured_store = app.config.get("RATING_STORE")
    if configured_store is None:
        configured_store = JsonlRatingStore(app.config["RATING_STORE_PATH"])
    app.extensions["knockknock_rating_store"] = configured_store

    def joke_json(joke: Joke) -> dict[str, object]:
        return {"id": joke.id, "name": joke.name}

    @app.get("/api/jokes")
    def api_jokes():
        return jsonify([joke_json(joke) for joke in JOKES])

    @app.get("/api/jokes/random")
    def api_random_joke():
        joke = random.choice(JOKES)
        return jsonify({**joke_json(joke), "lines": tell(joke)})

    @app.get("/api/jokes/<joke_id>")
    def api_joke_detail(joke_id: str):
        joke = _joke_by_id(joke_id)
        return jsonify({**joke_json(joke), "lines": tell(joke)})

    @app.post("/api/jokes/<joke_id>/ratings")
    def api_rate_joke(joke_id: str):
        joke = _joke_by_id(joke_id)
        payload = request.get_json(silent=True)
        submitted_value = payload.get("rating") if isinstance(payload, dict) else None
        try:
            rating = Rating.now(joke.id, submitted_value)
        except (TypeError, ValueError):
            return jsonify({"message": "Please choose a whole-number rating from 1 to 5."}), 400
        try:
            app.extensions["knockknock_rating_store"].save(rating)
        except OSError:
            return jsonify({"message": "Your rating could not be saved. Please try again later."}), 500
        return jsonify({"message": "Thanks for rating this joke!"}), 201

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
        return render_template("catalogue.html", jokes=JOKES)

    @app.get("/")
    def random_joke():
        if built_app_available():
            return send_from_directory(static_root, "index.html")
        joke = random.choice(JOKES)
        return render_template("joke.html", joke=joke, lines=tell(joke), random_page=True)

    @app.get("/jokes/<joke_id>")
    def joke_detail(joke_id: str):
        joke = _joke_by_id(joke_id)
        if built_app_available():
            return send_from_directory(static_root, "index.html")
        return render_template(
            "joke.html",
            joke=joke,
            lines=tell(joke),
            reveal_full=session.pop("reveal_full_joke", None) == joke.id,
        )

    @app.post("/jokes/<joke_id>/ratings")
    def rate_joke(joke_id: str):
        joke = _joke_by_id(joke_id)
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
            app.extensions["knockknock_rating_store"].save(rating)
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
