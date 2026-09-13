"""Command-line interface for the knock-knock joke system."""

import argparse
import random

from .jokes import JOKES, get_joke
from .sequence import tell

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

    # Keep explicit joke requests stable; the default mode gets a random style.
    title_lines = random.choice(ASCII_ART_FORMATS) if args.joke is None else TITLE_LINES
    print_title(title_lines)
    for line in tell(joke):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
