"""Command-line interface for the knock-knock joke system."""

import argparse
import logging
import random
import select
import sys
from pathlib import Path

from .jokes import JOKES, get_joke
from .sequence import tell
from .ratings import JsonlRatingStore, Rating, RatingStore

LOGGER = logging.getLogger(__name__)
RATING_INPUT_TIMEOUT_SECONDS = 10

# Generated in a fixed-width font so the title remains stable across terminals.
TITLE_LINES = [
    r" ____  __.                     __      ____  __.                     __    ",
    r"|    |/ _| ____   ____   ____ |  | __ |    |/ _| ____   ____   ____ |  | __",
    "|      <  /    \\ /  _ \\_/ ___\\|  |/ / |      <  /    \\ /  _ \\_/ ___\\|  |/ /",
    "|    |  \\|   |  (  <_> )  \\___|    <  |    |  \\|   |  (  <_> )  \\___|    < ",
    "|____|__ \\___|  /\\____/ \\___  >__|_ \\ |____|__ \\___|  /\\____/ \\___  >__|_ \\",
    "        \\/    \\/            \\/     \\/         \\/    \\/            \\/     \\/",
]

# Each style is a complete set of lines so it can be selected independently.
ASCII_ART_FORMATS = (
    TITLE_LINES,
    [
        r" _  __                 _                _    _            _",
        r"| |/ /___  _ __   ___  | | __  _ __     | |  | | ___   ___| | __",
        r"| ' // _ \\| '_ \\ / _ \\ | |/ / | '_ \\    | |  | |/ _ \\ / __| |/ /",
        r"| . \\ (_) | | | |  __/ |   <  | | | |   | |__| | (_) | (__|   < ",
        r"|_|\\_\\___/|_| |_|\\___| |_|\\_\\ |_| |_|    \\____/ \\___/ \\___|_|\\_\\",
        r"                 knock knock!",
    ],
    [
        "╔══════════════════════════════╗",
        "╔╦╗╔═╗╔╗╔╔═╗╔═╗╦╔═╔═╗╔╗╔╔═╗",
        " ║ ║ ║║║║║ ╦║ ║╠╩╗║╣ ║║║║ ╦",
        " ╩ ╚═╝╝╚╝╚═╝╚═╝╩ ╩╚═╝╝╚╝╚═╝",
        "╚══════════════════════════════╝",
        "            * * *",
    ],
    [
        "+----------------------------------+",
        "|          KNOCK KNOCK!             |",
        "|      +--------------------+       |",
        "|      |   ASCII surprise!  |       |",
        "|      +--------------------+       |",
        "+----------------------------------+",
    ],
)


def print_title(lines: list[str] = TITLE_LINES) -> None:
    for line in lines:
        print(line)


def _safe_diagnostic(value: str) -> str:
    """Keep user-controlled parser diagnostics free of terminal controls."""
    return "".join(character if character.isprintable() else f"\\x{ord(character):02x}" for character in value)


def _collect_rating(joke_id: str, store: RatingStore, input_stream=sys.stdin) -> None:
    """Prompt for a rating, allowing an empty answer or one retry."""
    if not input_stream.isatty():
        return
    for attempt in range(2):
        try:
            print("Rate this joke (1-5, or Enter to skip): ", end="", flush=True)
            try:
                ready, _, _ = select.select(
                    [input_stream], [], [], RATING_INPUT_TIMEOUT_SECONDS
                )
            except (OSError, ValueError):
                # Some test doubles and non-Unix streams do not expose a
                # selectable file descriptor; preserve their prior behavior.
                ready = [input_stream]
            if not ready:
                print()
                return
            answer = input_stream.readline()
            if answer == "":
                return
            answer = answer.rstrip("\r\n")
        except EOFError:
            return
        if not answer.strip():
            return
        try:
            rating = Rating.now(joke_id, int(answer.strip()))
        except (ValueError, TypeError):
            if attempt == 0:
                print("Please enter a number from 1 to 5, or press Enter to skip.", file=sys.stderr)
                continue
            print("Rating skipped.", file=sys.stderr)
            return
        try:
            store.save(rating)
        except OSError as error:
            print(f"Rating could not be saved: {error}", file=sys.stderr)
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Tell a knock-knock joke.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="list all available jokes")
    group.add_argument("--joke", metavar="INDEX_OR_NAME", help="tell a joke by index or name")
    parser.add_argument("--rate", action="store_true", help="optionally rate the joke interactively")
    parser.add_argument("--rating-store", metavar="PATH", help="JSONL file for ratings (used with --rate)")
    args = parser.parse_args()

    if args.list:
        print_title()
        for index, joke in enumerate(JOKES):
            print(f"{index}: {joke.name}")
        return 0

    if args.joke is None:
        joke = random.choice(JOKES)
    else:
        try:
            try:
                selector = int(args.joke)
            except ValueError:
                selector = args.joke
            joke = get_joke(selector)
        except (IndexError, KeyError) as error:
            parser.error(_safe_diagnostic(str(error).strip("'")))

    # Keep explicit joke requests stable; the default mode gets a random style.
    title_lines = random.choice(ASCII_ART_FORMATS) if args.joke is None else TITLE_LINES
    LOGGER.info("Served joke: %s", joke.name)
    print_title(title_lines)
    for line in tell(joke):
        print(line)
    if args.rate:
        default_path = Path.home() / ".local" / "share" / "knockknock" / "ratings.jsonl"
        _collect_rating(joke.id, JsonlRatingStore(args.rating_store or default_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
