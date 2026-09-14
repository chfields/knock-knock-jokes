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


def test_rating_prompt_uses_configured_timeout(monkeypatch):
    store = Store()
    calls = []
    monkeypatch.setenv("KNOCK_KNOCK_RATING_SKIP_SECONDS", "2.5")

    def no_input(streams, writable, exceptional, timeout):
        calls.append(timeout)
        return [], [], []

    monkeypatch.setattr(cli.select, "select", no_input)

    cli._collect_rating("joke", store, TTYInput("5\n"))

    assert calls == [2.5]
    assert store.ratings == []


def test_rating_prompt_uses_cli_timeout_over_environment(monkeypatch):
    store = Store()
    calls = []
    monkeypatch.setenv("KNOCK_KNOCK_RATING_SKIP_SECONDS", "2.5")

    def no_input(streams, writable, exceptional, timeout):
        calls.append(timeout)
        return [], [], []

    monkeypatch.setattr(cli.select, "select", no_input)

    cli._collect_rating("joke", store, TTYInput("5\n"), skip_seconds=1.25)

    assert calls == [1.25]
    assert store.ratings == []


def test_rating_prompt_ignores_invalid_configured_timeout(monkeypatch):
    store = Store()
    calls = []
    monkeypatch.setenv("KNOCK_KNOCK_RATING_SKIP_SECONDS", "not-a-number")

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
