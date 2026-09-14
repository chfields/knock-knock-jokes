"""Rating validation and append-only local storage."""

import json
import logging
import stat
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, Union

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Rating:
    """A validated rating for one joke."""

    joke_id: str
    value: int
    timestamp: str

    def __post_init__(self) -> None:
        if not isinstance(self.joke_id, str) or not self.joke_id.strip():
            raise ValueError("Joke ID must be a non-empty string")
        if isinstance(self.value, bool) or not isinstance(self.value, int) or not 1 <= self.value <= 5:
            raise ValueError("Rating must be an integer from 1 to 5")
        if not isinstance(self.timestamp, str) or not self.timestamp.strip():
            raise ValueError("Rating timestamp must be a non-empty string")

    @classmethod
    def now(cls, joke_id: str, value: int) -> "Rating":
        return cls(joke_id, value, datetime.now(timezone.utc).isoformat())


class RatingStore(Protocol):
    def save(self, rating: Rating) -> None:
        """Persist one rating."""


class JsonlRatingStore:
    """Persist ratings as one JSON object per line."""

    def __init__(self, path: Union[Path, str]) -> None:
        self.path = Path(path)

    def save(self, rating: Rating) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and not self.path.stat().st_mode & (
            stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
        ):
            LOGGER.warning("Rating store %s is missing write permission", self.path)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(asdict(rating), sort_keys=True) + "\n")
