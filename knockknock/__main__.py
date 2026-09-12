"""Command-line interface for the knock-knock joke system."""

import argparse
import random

from .jokes import JOKES, get_joke
from .sequence import tell

TITLE_LINES = [
    "+-----------------------+",
    "|   Knock Knock Jokes   |",
    "+-----------------------+",
]


def print_title() -> None:
    print("\n".join(TITLE_LINES))


def main() -> int:
    parser = argparse.ArgumentParser(description="Tell a knock-knock joke.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="list all available jokes")
    group.add_argument("--joke", metavar="INDEX_OR_NAME", help="tell a joke by index or name")
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
            parser.error(str(error).strip("'"))

    print_title()
    print("\n".join(tell(joke)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
