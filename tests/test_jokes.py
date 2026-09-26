import pytest

from knockknock.jokes import JOKES, Joke, get_joke


def test_joke_bank_has_32_unique_well_formed_jokes():
    assert len(JOKES) == 32
    assert all(isinstance(joke, Joke) for joke in JOKES)
    assert all(joke.name.strip() and joke.punchline.strip() for joke in JOKES)
    assert len({joke.name.casefold() for joke in JOKES}) == len(JOKES)
    assert len({joke.id for joke in JOKES}) == len(JOKES)


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
    assert get_joke("cows") == Joke("Cows", "Bless you!", "cows")


@pytest.mark.parametrize("selector", [-1, len(JOKES), "not-a-joke"])
def test_get_joke_rejects_unknown_selector(selector):
    with pytest.raises((IndexError, KeyError)):
        get_joke(selector)
