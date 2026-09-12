"""Turn joke data into the familiar call-and-response lines."""

from .jokes import Joke


def tell(joke: Joke) -> list[str]:
    """Build the five lines used to tell *joke*."""
    return [
        "Knock knock.",
        "Who's there?",
        f"{joke.name}.",
        f"{joke.name} who?",
        joke.punchline,
    ]
