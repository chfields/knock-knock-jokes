import pytest

from knockknock.jokes import JOKES, VEGETABLE_JOKE_IDS, Joke, get_joke


def test_joke_bank_has_62_unique_well_formed_jokes():
    assert len(JOKES) == 62
    assert all(isinstance(joke, Joke) for joke in JOKES)
    assert all(joke.name.strip() and joke.punchline.strip() for joke in JOKES)
    assert len({joke.name.casefold() for joke in JOKES}) == len(JOKES)
    assert len({joke.id for joke in JOKES}) == len(JOKES)


def test_all_twenty_four_vegetable_jokes_load():
    vegetable_jokes = {joke.id: joke for joke in JOKES if joke.id in VEGETABLE_JOKE_IDS}

    assert VEGETABLE_JOKE_IDS == {
        "artichoke", "asparagus", "beet", "broccoli", "carrot", "cauliflower",
        "celery", "corn", "cucumber", "eggplant", "garlic", "green-bean", "kale",
        "leek", "onion", "pea", "pepper", "potato", "radish", "spinach", "squash",
        "sweet-potato", "turnip", "zucchini",
    }
    assert len(vegetable_jokes) == 24
    assert all(joke.name and joke.punchline for joke in vegetable_jokes.values())


def test_get_joke_supports_zero_based_index_and_name():
    assert get_joke(0) is JOKES[0]
    assert get_joke(JOKES[0].name.upper()) is JOKES[0]


def test_get_joke_includes_orange_joke():
    assert get_joke("orange") == Joke(
        "Orange", "Orange you glad I didn't say banana?", "orange"
    )


def test_get_joke_includes_duck_joke():
    assert get_joke("duck") == Joke(
        "Duck", "Duck you want to hear another joke?", "duck"
    )


def test_get_joke_includes_cow_joke():
    assert get_joke("cows") == Joke("Cows", "Cows go moo, that's why I knocked!", "cows")


def test_get_joke_includes_quack_joke():
    assert get_joke("quack") == Joke(
        "Quack", "Quack the door open, it's cold out here!", "quack"
    )


def test_get_joke_includes_little_old_lady_joke():
    assert get_joke("a little old lady") == Joke(
        "A little old lady",
        "I didn't know you could yodel!",
        "a-little-old-lady",
    )


@pytest.mark.parametrize(
    ("name", "punchline", "joke_id"),
    [
        ("Justin", "Justin time for dinner!", "justin"),
        ("Harry", "Harry up and open the door, it's cold!", "harry"),
        ("Ice cream", "Ice cream every time I see a ghost!", "ice-cream"),
    ],
)
def test_get_joke_includes_new_jokes(name, punchline, joke_id):
    assert get_joke(name) == Joke(name, punchline, joke_id)


@pytest.mark.parametrize("selector", [-1, len(JOKES), "not-a-joke"])
def test_get_joke_rejects_unknown_selector(selector):
    with pytest.raises((IndexError, KeyError)):
        get_joke(selector)
