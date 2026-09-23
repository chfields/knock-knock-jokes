import json

import pytest

from knockknock.ratings import JsonlRatingStore, Rating, average_rating, rating_count


def test_rating_count_returns_zero_for_empty_ratings():
    assert rating_count([], "joke") == 0


def test_rating_count_returns_zero_for_non_matching_ratings():
    ratings = [Rating("other", 4, "now")]

    assert rating_count(ratings, "joke") == 0


def test_rating_count_returns_one_for_single_matching_rating():
    ratings = [Rating("joke", 4, "now")]

    assert rating_count(ratings, "joke") == 1


def test_rating_count_returns_number_of_matching_ratings():
    ratings = [Rating("joke", 2, "now"), Rating("joke", 5, "later")]

    assert rating_count(ratings, "joke") == 2


def test_rating_count_excludes_ratings_for_different_jokes():
    ratings = [Rating("joke", 2, "now"), Rating("other", 5, "later"), Rating("joke", 4, "after")]

    assert rating_count(ratings, "joke") == 2


def test_average_rating_returns_none_for_empty_or_non_matching_ratings():
    assert average_rating([], "joke") is None
    assert average_rating([Rating("other", 4, "now")], "joke") is None


def test_average_rating_returns_single_matching_value_as_float():
    result = average_rating([Rating("joke", 4, "now")], "joke")

    assert result == 4.0
    assert isinstance(result, float)


def test_average_rating_returns_mean_of_matching_ratings():
    ratings = [Rating("joke", 2, "now"), Rating("joke", 5, "later")]

    assert average_rating(ratings, "joke") == 3.5


def test_average_rating_excludes_ratings_for_different_jokes():
    ratings = [Rating("joke", 2, "now"), Rating("other", 5, "later")]

    assert average_rating(ratings, "joke") == 2.0


def test_rating_rejects_values_outside_one_to_five():
    with pytest.raises(ValueError):
        Rating("joke", 6, "now")


def test_store_writes_jsonl(tmp_path):
    path = tmp_path / "ratings.jsonl"
    JsonlRatingStore(path).save(Rating("joke", 4, "now"))
    assert json.loads(path.read_text()) == {"joke_id": "joke", "timestamp": "now", "value": 4}


def test_store_warns_when_file_has_no_write_permission(tmp_path, caplog):
    path = tmp_path / "ratings.jsonl"
    path.write_text("")
    path.chmod(0o444)

    with caplog.at_level("WARNING"):
        try:
            JsonlRatingStore(path).save(Rating("joke", 4, "now"))
        except OSError:
            pass

    assert f"Rating store {path} is missing write permission" in caplog.text
