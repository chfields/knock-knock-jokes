import pytest

from knockknock.jokes import JOKES, Joke, get_joke, joke_count


def test_joke_bank_has_eight_unique_well_formed_jokes():
    assert len(JOKES) >= 8
    assert all(isinstance(joke, Joke) for joke in JOKES)
    assert all(joke.name.strip() and joke.punchline.strip() for joke in JOKES)
    assert len({joke.name.casefold() for joke in JOKES}) == len(JOKES)


def test_joke_count_returns_zero_for_empty_iterable():
    assert joke_count(()) == 0


def test_joke_count_returns_one_for_single_joke():
    assert joke_count((JOKES[0],)) == 1


def test_joke_count_returns_number_of_several_jokes():
    assert joke_count(JOKES[:3]) == 3


def test_get_joke_supports_zero_based_index_and_name():
    assert get_joke(0) is JOKES[0]
    assert get_joke(JOKES[0].name.upper()) is JOKES[0]


@pytest.mark.parametrize("selector", [-1, len(JOKES), "not-a-joke"])
def test_get_joke_rejects_unknown_selector(selector):
    with pytest.raises((IndexError, KeyError)):
        get_joke(selector)
