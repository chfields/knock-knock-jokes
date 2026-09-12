# Design

The project is deliberately split into three small layers:

- `jokes.py` owns the immutable `Joke` value object, the catalogue, and lookup.
- `sequence.py` turns a `Joke` into a plain five-line list. Keeping formatting out of the catalogue makes the core behavior easy to test and reuse.
- `__main__.py` handles argument parsing, random selection, and terminal output. It delegates all joke data and sequence construction to the package layers.

The catalogue is a tuple of frozen dataclasses, so callers cannot accidentally mutate the shared bank. Names are unique and lookup by name is case-insensitive; indexes are zero-based to match Python conventions. The CLI uses `--list` for discovery, `--joke` for deterministic selection, and random choice when no option is provided.
