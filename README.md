# Knock-knock jokes

A small Python package and command-line program for telling classic knock-knock jokes.

## Install

From this repository, install the package in editable mode:

```bash
python -m pip install -e .
```

## Usage

Tell a random joke:

```bash
python -m knockknock
```

List the available jokes:

```bash
python -m knockknock --list
```

Tell a joke by its zero-based index or setup name:

```bash
python -m knockknock --joke 0
python -m knockknock --joke Lettuce
```

An optional JSON configuration file can be supplied at startup:

```bash
python -m knockknock --config config.json --rate
```

The supported setting is `rating_store`, which is overridden by an explicit
`--rating-store` argument. The config path must exist and refer to a file.

Ratings are optional. Enable the interactive prompt with `--rate`; press Enter
to skip, or enter a number from 1 to 5. In an interactive CLI, the prompt also
skips automatically after 10 seconds with no input. In a non-interactive CLI,
rating collection is skipped by default without prompting. Invalid input gets
one retry and is then skipped.
Set `KNOCK_KNOCK_RATING_SKIP_SECONDS` to change the interactive prompt timeout.
You can override it for one invocation with `--skip-seconds`, for example
`python -m knockknock --rate --skip-seconds 3`.
To persist this setting across sessions, add it to your shell's configuration
file, such as `~/.profile`.
Ratings are appended to
`~/.local/share/knockknock/ratings.jsonl` (or a path supplied with
`--rating-store`) and are never requested by default or by `--list`. The file
is local append-only history; remove it when ratings should be discarded.

The same functionality is available through the installed `knockknock` command.

## Development

Run the test suite with `pytest`:

```bash
pytest
```
