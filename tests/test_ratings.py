import json

import pytest

from knockknock.ratings import JsonlRatingStore, Rating


def test_rating_rejects_values_outside_one_to_five():
    with pytest.raises(ValueError):
        Rating("joke", 6, "now")


def test_store_writes_jsonl(tmp_path):
    path = tmp_path / "ratings.jsonl"
    JsonlRatingStore(path).save(Rating("joke", 4, "now"))
    assert json.loads(path.read_text()) == {"joke_id": "joke", "timestamp": "now", "value": 4}
