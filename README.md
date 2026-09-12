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

The same functionality is available through the installed `knockknock` command.

## Development

Run the test suite with `pytest`:

```bash
pytest
```
