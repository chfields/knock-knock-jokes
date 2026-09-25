"""The joke catalogue and lookup helpers."""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Joke:
    """A setup word or phrase and the line that completes its joke."""

    name: str
    punchline: str
    id: str = ""

    def __post_init__(self) -> None:
        """Reject malformed catalogue values at the boundary."""
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Joke name must be a non-empty string")
        if not isinstance(self.punchline, str) or not self.punchline.strip():
            raise ValueError("Joke punchline must be a non-empty string")
        if self.id == "":
            object.__setattr__(self, "id", self.name.casefold().replace(" ", "-"))
        elif not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Joke ID must be a non-empty string")


JOKES: tuple[Joke, ...] = (
    Joke("Cow says", "No, a cow says moo!", "cow-says"),
    Joke("Lettuce", "Lettuce in, it's cold out here!", "lettuce"),
    Joke("Boo", "Don't cry, it's only a joke!", "boo"),
    Joke("Tank", "You're welcome!", "tank"),
    Joke("Dwayne", "Dwayne the bathtub, I'm dwowning!", "dwayne"),
    Joke("Atch", "Bless you!", "atch"),
    Joke("Nobel", "Nobel, that's why I knocked!", "nobel"),
    Joke("Olive", "Olive you and I miss you!", "olive"),
    Joke("Cargo", "Car go!", "cargo"),
    Joke("Canoe", "Canoe help me with my homework?", "canoe"),
    Joke("Annie", "Annie body home?", "annie"),
    Joke("Howard", "Howard you like to hear a joke?", "howard"),
    Joke("Europe", "Europe!", "europe"),
    Joke("Wooden shoe", "Wooden shoe like to hear another joke?", "wooden-shoe"),
    Joke("Control freak", "Control freak!", "control-freak"),
    Joke("Interrupting cow", "Moo!", "interrupting-cow"),
    Joke("Hatch", "Bless you!", "hatch"),
    Joke("Spell", "W-H-O.", "spell"),
    Joke("Police", "Police let me in!", "police"),
    Joke("Al", "Al give you a call later.", "al"),
    Joke("Ya", "Ya!", "ya"),
    Joke("Figs", "Figs the doorbell, that's why I knocked!", "figs"),
    Joke("A herd", "A herd you were home!", "a-herd"),
    Joke("Snow", "Snow use, the door is locked!", "snow"),
    Joke("Needle", "Needle little money!", "needle"),
    Joke("Adore", "Adore is between us, so open the door!", "adore"),
    Joke("Dishes", "Dishes Sean Connery!", "dishes"),
    Joke("Cash", "Cash! Cash who? No thanks, I'll have a little later.", "cash"),
    Joke("Sundae", "Sundae or later, you have to let me in!", "sundae"),
)


def get_joke(selector: Union[int, str]) -> Joke:
    """Return a joke by zero-based index or case-insensitive name."""
    if isinstance(selector, bool):
        raise TypeError("Joke selector must be an integer or string")
    if isinstance(selector, int):
        if selector < 0:
            raise IndexError(f"No joke at index {selector}")
        try:
            return JOKES[selector]
        except IndexError as error:
            raise IndexError(f"No joke at index {selector}") from error

    if not isinstance(selector, str):
        raise TypeError("Joke selector must be an integer or string")

    normalized = selector.casefold()
    for joke in JOKES:
        if joke.name.casefold() == normalized:
            return joke
    raise KeyError(f"Unknown joke: {selector}")
