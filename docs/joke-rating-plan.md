# Joke rating plan

## Goal

After a joke is printed, let the user optionally rate it from 1 to 5 stars.
The existing non-interactive and listing flows should remain unchanged unless
the user explicitly enables rating.

## Proposed flow

1. Add an opt-in `--rate` CLI flag for an interactive session.
2. Print `Rate this joke (1-5, or Enter to skip): ` after the punchline.
3. Accept only a single integer from 1 through 5; show a short error and allow
   one retry for invalid input, then continue without recording a rating.
4. Associate the submitted rating with the served joke's stable identifier and
   timestamp, not its display text.
5. Cap ratings at one submission per joke per session.

## Implementation slices

- Add a stable joke ID and a small rating value object/validator in the domain
  layer; keep ratings immutable and reject values outside 1-5.
- Put persistence behind a `RatingStore` interface. Start with a local,
  append-only JSON-lines store whose path is configurable, and fail gracefully
  if it cannot be written.
- Keep prompting and terminal input in the CLI layer. Do not prompt for
  `--list`, redirected/non-interactive input, or existing commands without
  `--rate`.
- Add documentation for enabling ratings, the storage location, skipped
  ratings, and privacy/retention expectations.

## Verification

Add unit tests for validation and store serialization, plus CLI tests for a
valid rating, skipped input, invalid input, write failure, and unchanged
default/list behavior. Run the existing test suite and confirm ratings are
never required to serve a joke.
