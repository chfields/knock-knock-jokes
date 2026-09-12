import subprocess
import sys

from knockknock.__main__ import TITLE
from knockknock.jokes import JOKES

TITLE_LINES = TITLE.strip("\n").splitlines()
JOKE_LINE_COUNT = 5


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "knockknock", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_lists_all_jokes():
    result = run_cli("--list")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines()[: len(TITLE_LINES)] == TITLE_LINES
    assert all(f"{index}: {joke.name}" in result.stdout for index, joke in enumerate(JOKES))


def test_cli_tells_joke_by_index():
    result = run_cli("--joke", "0")

    assert result.returncode == 0
    assert result.stdout.splitlines() == TITLE_LINES + [
        "Knock knock.",
        "Who's there?",
        f"{JOKES[0].name}.",
        f"{JOKES[0].name} who?",
        JOKES[0].punchline,
    ]


def test_cli_tells_joke_by_name():
    result = run_cli("--joke", JOKES[1].name)

    assert result.returncode == 0
    assert result.stdout.splitlines()[: len(TITLE_LINES)] == TITLE_LINES
    assert f"{JOKES[1].name} who?" in result.stdout


def test_cli_defaults_to_a_joke():
    result = run_cli()

    assert result.returncode == 0
    assert len(result.stdout.splitlines()) == len(TITLE_LINES) + JOKE_LINE_COUNT


def test_cli_reports_invalid_joke():
    result = run_cli("--joke", "does-not-exist")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "Unknown joke" in result.stderr


def test_cli_reports_negative_index():
    result = run_cli("--joke", "-1")

    assert result.returncode != 0
    assert "No joke at index -1" in result.stderr
