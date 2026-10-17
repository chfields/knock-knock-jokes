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
    Joke("Orange", "Orange you glad I didn't say banana?", "orange"),
    Joke("Duck", "Duck you want to hear another joke?", "duck"),
    Joke("Cows", "Cows go moo, that's why I knocked!", "cows"),
    Joke("Quack", "Quack the door open, it's cold out here!", "quack"),
    Joke(
        "A little old lady",
        "I didn't know you could yodel!",
        "a-little-old-lady",
    ),
    Joke("Meow", "Cat got your tongue?", "cat"),
    Joke("Justin", "Justin time for dinner!", "justin"),
    Joke("Harry", "Harry up and open the door, it's cold!", "harry"),
    Joke("Ice cream", "Ice cream every time I see a ghost!", "ice-cream"),
    Joke("Artichoke", "Artie choke on my vegetable jokes!", "artichoke"),
    Joke("Asparagus", "Asparagus in, this joke is growing on you!", "asparagus"),
    Joke("Beet", "Beet it, this is a vegetable-only doorway!", "beet"),
    Joke("Broccoli", "Broccoli your calendar; it's time for dinner!", "broccoli"),
    Joke("Carrot", "Carrot wait to tell you this joke!", "carrot"),
    Joke("Cauliflower", "Cauli-for your attention, please!", "cauliflower"),
    Joke("Celery", "Celery-brate, because dinner is ready!", "celery"),
    Joke("Corn", "Corn you open the door?", "corn"),
    Joke("Cucumber", "Cucumber in; it is chilly out here!", "cucumber"),
    Joke("Eggplant", "Eggplant a kiss on the door before you open it!", "eggplant"),
    Joke("Garlic", "Garlic you to let me in!", "garlic"),
    Joke("Green bean", "Green bean waiting for you all day!", "green-bean"),
    Joke("Kale", "Kale me maybe when you open the door!", "kale"),
    Joke("Leek", "Leek before you open the door!", "leek"),
    Joke("Onion", "Onion way you can leave me outside!", "onion"),
    Joke("Pea", "Pea-lease let me in!", "pea"),
    Joke("Pepper", "Pepper-mint tea is waiting inside!", "pepper"),
    Joke("Potato", "Potato you later, but first open the door!", "potato"),
    Joke("Radish", "Radish the door, I am ready for dinner!", "radish"),
    Joke("Spinach", "Spinach your seat; I have a joke to tell!", "spinach"),
    Joke("Squash", "Squash the idea that I am leaving!", "squash"),
    Joke("Sweet potato", "Sweet potato you open the door for me?", "sweet-potato"),
    Joke("Turnip", "Turnip the volume; this joke is a good one!", "turnip"),
    Joke("Zucchini", "Zucchini me at the dinner table!", "zucchini"),
)


VEGETABLE_JOKE_IDS: frozenset[str] = frozenset(
    {
        "artichoke",
        "asparagus",
        "beet",
        "broccoli",
        "carrot",
        "cauliflower",
        "celery",
        "corn",
        "cucumber",
        "eggplant",
        "garlic",
        "green-bean",
        "kale",
        "leek",
        "onion",
        "pea",
        "pepper",
        "potato",
        "radish",
        "spinach",
        "squash",
        "sweet-potato",
        "turnip",
        "zucchini",
    }
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
