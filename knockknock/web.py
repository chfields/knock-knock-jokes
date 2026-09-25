"""Optional Flask web front end for the joke catalogue."""

import random
from pathlib import Path
from typing import Mapping, Optional

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

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

    @app.get("/")
    def random_joke():
        joke = random.choice(JOKES)
        return render_template("joke.html", joke=joke, lines=tell(joke), random_page=True)

    @app.get("/jokes")
    def catalogue():
        return render_template("catalogue.html", jokes=JOKES)

    @app.get("/jokes/<joke_id>")
    def joke_detail(joke_id: str):
        joke = _joke_by_id(joke_id)
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
