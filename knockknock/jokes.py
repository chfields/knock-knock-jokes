"""The joke catalogue and lookup helpers."""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Joke:
    """A setup word or phrase and the line that completes its joke."""

    name: str
    punchline: str


JOKES = (
    Joke("Cow says", "No, a cow says moo!"),
    Joke("Lettuce", "Lettuce in, it's cold out here!"),
    Joke("Boo", "Don't cry, it's only a joke!"),
    Joke("Tank", "You're welcome!"),
    Joke("Dwayne", "Dwayne the bathtub, I'm dwowning!"),
    Joke("Atch", "Bless you!"),
    Joke("Nobel", "Nobel, that's why I knocked!"),
    Joke("Olive", "Olive you and I miss you!"),
)


def get_joke(selector: Union[int, str]) -> Joke:
    """Return a joke by zero-based index or case-insensitive name."""
    if isinstance(selector, int):
        if selector < 0:
            raise IndexError(f"No joke at index {selector}")
        try:
            return JOKES[selector]
        except IndexError as error:
            raise IndexError(f"No joke at index {selector}") from error

    normalized = selector.casefold()
    for joke in JOKES:
        if joke.name.casefold() == normalized:
            return joke
    raise KeyError(f"Unknown joke: {selector}")
