from knockknock import __main__ as cli


class TTYInput:
    def __init__(self, answer):
        self.answer = answer

    def isatty(self):
        return True

    def readline(self):
        return self.answer


class Store:
    def __init__(self):
        self.ratings = []

    def save(self, rating):
        self.ratings.append(rating)


def test_rating_prompt_skips_after_timeout(monkeypatch):
    store = Store()
    calls = []

    def no_input(streams, writable, exceptional, timeout):
        calls.append(timeout)
        return [], [], []

    monkeypatch.setattr(cli.select, "select", no_input)

    cli._collect_rating("joke", store, TTYInput("5\n"))

    assert calls == [10]
    assert store.ratings == []


def test_rating_prompt_still_saves_available_input(monkeypatch):
    store = Store()
    monkeypatch.setattr(cli.select, "select", lambda *args: ([args[0][0]], [], []))

    cli._collect_rating("joke", store, TTYInput("5\n"))

    assert [rating.value for rating in store.ratings] == [5]
