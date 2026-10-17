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
    Joke("Llama", "Llama know when you open the door!", "llama"),
    Joke("Bee", "Bee-have and open the door!", "bee"),
    Joke("Chicken", "Chicken on you to open up!", "chicken"),
    Joke("Deer", "Deer me, it's chilly out here!", "deer"),
    Joke("Elephant", "Elephant you let me in?", "elephant"),
    Joke("Frog", "Frog-et the doorbell, I knocked!", "frog"),
    Joke("Giraffe", "Giraffe me a hand and open the door!", "giraffe"),
    Joke("Horse", "Horse the rush? I can wait inside!", "horse"),
    Joke("Kangaroo", "Kangaroo let me in before I hop away?", "kangaroo"),
    Joke("Lion", "Lion around won't get this door open!", "lion"),
    Joke("Monkey", "Monkey see, monkey do—open the door!", "monkey"),
    Joke("Owl", "Owl be warm once you let me in!", "owl"),
    Joke("Penguin", "Penguin me a coat, it's freezing!", "penguin"),
    Joke("Rabbit", "Rabbit up, I have a joke to tell!", "rabbit"),
    Joke("Sheep", "Sheep it simple and let me in!", "sheep"),
    Joke("Tiger", "Tiger up this joke, it's a good one!", "tiger"),
    Joke("Turtle", "Turtle-y ready to come inside!", "turtle"),
    Joke("Walrus", "Walrus you waiting for? Open the door!", "walrus"),
    Joke("Bison", "Bison time you opened the door!", "bison"),
    Joke("Zebra", "Zebra me in from the cold!", "zebra"),
    Joke("Brazil", "Brazil yourself, this joke is funny!", "brazil"),
    Joke("Chile", "Chile out here, so please let me in!", "chile"),
    Joke("China", "China be a dear and open the door?", "china"),
    Joke("Denmark", "Denmark's the doorbell, that's why I knocked!", "denmark"),
    Joke("Egypt", "Egypting cold out here!", "egypt"),
    Joke("Finland", "Finland a way to get you to open up!", "finland"),
    Joke("France", "France, I thought you'd never open the door!", "france"),
    Joke("Greece", "Greece the hinges, this door is stuck!", "greece"),
    Joke("Hungary", "Hungary for a joke?", "hungary"),
    Joke("India", "India hurry to hear a knock-knock joke?", "india"),
    Joke("Iran", "I ran all the way here to tell you a joke!", "iran"),
    Joke("Japan", "Japan the door, it's getting cold!", "japan"),
    Joke("Kenya", "Kenya let me in before it rains?", "kenya"),
    Joke("Laos", "Laos me in, I've got a joke!", "laos"),
    Joke("Mali", "Mali Christmas! I brought a joke!", "mali"),
    Joke("Mexico", "Mexico wild when I tell this joke!", "mexico"),
    Joke("Nepal", "Nepal a hand and open the door!", "nepal"),
    Joke("Oman", "Oman, it's cold out here!", "oman"),
    Joke("Peru", "Peru-sual knock-knock joke coming up!", "peru"),
    Joke("Thailand", "Thai-land of knocking has brought you a joke!", "thailand"),
)


CATEGORY_JOKE_IDS = {
    "animals": (
        "llama", "bee", "chicken", "deer", "elephant", "frog", "giraffe",
        "horse", "kangaroo", "lion", "monkey", "owl", "penguin", "rabbit",
        "sheep", "tiger", "turtle", "walrus", "bison", "zebra",
    ),
    "countries": (
        "brazil", "chile", "china", "denmark", "egypt", "finland", "france",
        "greece", "hungary", "india", "iran", "japan", "kenya", "laos", "mali",
        "mexico", "nepal", "oman", "peru", "thailand",
    ),
}


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
