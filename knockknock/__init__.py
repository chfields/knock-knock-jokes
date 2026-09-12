"""A small, testable knock-knock joke system."""

from .jokes import JOKES, Joke, get_joke
from .sequence import tell

__all__ = ["JOKES", "Joke", "get_joke", "tell"]
