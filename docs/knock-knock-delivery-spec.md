# Knock-Knock Delivery Specification

**Status:** Proposed
**Owner:** Knock Knock Jokes contributors
**Audience:** Maintainers, contributors, and reviewers
**Scope:** The `knockknock` Python package and its command-line interface

## 1. Summary

Deliver a small, dependency-free Python application that tells classic
knock-knock jokes from a built-in catalogue. A user can ask for a random joke,
list the catalogue, or select a joke deterministically by zero-based index or
case-insensitive name. The package API must remain usable without invoking the
CLI, and the CLI must remain a thin presentation layer over the package.

The current implementation is the reference behavior for this specification:
the catalogue is immutable, a joke is rendered as five call-and-response
lines, and invalid selections produce a concise non-zero CLI failure.

## 2. Goals and non-goals

### Goals

- Make the common action (`python -m knockknock`) immediately useful with no
  arguments or external services.
- Provide deterministic selection for demonstrations, tests, and scripts.
- Keep joke data, sequence construction, and terminal concerns in separate
  modules.
- Make catalogue lookup predictable and safe for arbitrary user input.
- Preserve a small standard-library-only runtime footprint.
- Ship behavior that can be verified through automated tests and documented
  command examples.

### Non-goals

- Network-delivered, user-generated, or remotely synchronized jokes.
- Persistent user preferences, history, ratings, or authentication.
- Interactive input after process startup.
- Localization, accessibility narration, or rich terminal dependencies.
- A plugin system or a general content-management abstraction.

## 3. User experience

### Default mode

Command:

```text
python -m knockknock
```

The program selects one catalogue entry at random, prints a title treatment,
then prints exactly this five-line sequence:

1. `Knock knock.`
2. `Who's there?`
3. `<name>.`
4. `<name> who?`
5. `<punchline>`

Default mode may vary its title treatment between invocations. The selected
joke and title do not need to be reproducible unless a future seeded mode is
explicitly added.

### Listing mode

Command:

```text
python -m knockknock --list
```

Print the title followed by one entry per joke in catalogue order. Each entry
must use the format `<zero-based index>: <name>`. Listing must exit with status
0 and must not tell a joke.

### Explicit selection mode

Commands:

```text
python -m knockknock --joke 0
python -m knockknock --joke Lettuce
python -m knockknock --joke lettuce
```

An integer selects by zero-based index; any other selector is matched against a
joke name case-insensitively. Explicit selection uses the stable default title
treatment and the same five-line sequence as default mode.

### Invalid input

- Negative or out-of-range indexes fail with a human-readable `No joke at
  index <value>` message.
- Unknown names fail with `Unknown joke: <value>`.
- `--list` and `--joke` are mutually exclusive.
- Standard argument-parser failures must use a non-zero exit status and write
  diagnostics to stderr without a traceback.
- Invalid input must not print a partial title or joke to stdout.

## 4. Functional requirements

### Catalogue and domain model

1. A joke consists of a non-empty display `name` and non-empty `punchline`.
2. Joke values are immutable after construction.
3. The catalogue is ordered and cannot be mutated through the public package
   value.
4. Catalogue names are unique under case-folded comparison.
5. The catalogue contains at least eight jokes at initial delivery.
6. `get_joke(selector)` accepts an integer or string and returns the matching
   `Joke`; unsupported or missing selectors raise a documented lookup error.
7. Integer lookup must reject negative values rather than Python's negative
   indexing behavior.

### Sequence builder

1. `tell(joke)` returns a new list containing exactly five strings.
2. The builder must not mutate the supplied `Joke` or catalogue.
3. Formatting belongs in the sequence module, not in catalogue storage.

### CLI

1. The module entry point and installed `knockknock` script invoke the same
   `main()` function.
2. `main()` returns `0` on successful list or joke delivery.
3. Random selection uses only the in-memory catalogue.
4. Output is plain terminal text and contains no control sequences originating
   from user input.
5. The CLI must not require network access, a writable filesystem, or runtime
   configuration.
6. Each successfully served joke must be recorded in the application log with
   the joke identity and a timestamp.

## 5. Public interfaces

The following interfaces are part of the initial package contract:

```python
@dataclass(frozen=True)
class Joke:
    name: str
    punchline: str

JOKES: tuple[Joke, ...]

def get_joke(selector: int | str) -> Joke: ...
def tell(joke: Joke) -> list[str]: ...
def main() -> int: ...
```

The package should continue exporting `Joke`, `JOKES`, `get_joke`, and `tell`.
Changes to selector semantics, output wording, or the five-line sequence are
breaking changes and require an explicit versioning decision.

## 6. Quality, security, and operational requirements

- Support the Python versions declared in `pyproject.toml`.
- Keep runtime dependencies empty unless a dependency is justified by a
  concrete requirement and reviewed for supply-chain impact.
- Run unit and CLI tests in CI on the supported Python matrix.
- Run linting and security checks already configured for the project.
- Keep user-provided selector text out of shell commands, paths, dynamic code,
  and format-string evaluation.
- If externally supplied jokes are introduced later, add input length limits,
  control-character handling, and provenance validation before changing this
  contract.
- Document any change to the catalogue or output contract alongside its tests.

## 7. Acceptance criteria

Delivery is accepted when all of the following are true:

- Running the default command succeeds and prints a title plus exactly five
  joke lines.
- `--list` prints every catalogue entry once, in stable order, with indexes
  starting at zero.
- A valid index, valid name, and case-variant name each select the expected
  joke.
- Each successfully served joke is recorded in the application log with a
  timestamp.
- Negative indexes, out-of-range indexes, unknown names, conflicting options,
  and malformed options fail cleanly with non-zero status.
- The package API returns immutable catalogue values and the expected sequence.
- Tests cover successful and failure paths, including empty and very large
  selectors where the argument parser permits them.
- The documented install and usage commands work from a clean environment
  without network access at runtime.
- CI quality and security checks pass.

## 8. Test plan

### Unit tests

- Validate joke fields, catalogue cardinality, ordering, immutability, and
  case-folded name uniqueness.
- Exercise first, last, negative, and out-of-range integer selectors.
- Exercise exact, mixed-case, empty, and unknown name selectors.
- Verify the five output lines for representative joke values.

### CLI contract tests

- Run default, list, index, and name modes as subprocesses.
- Assert stdout/stderr separation and exit status.
- Assert invalid selections do not emit partial stdout.
- Assert each successfully served joke creates a log entry containing its
  identity and a timestamp.
- Assert conflicting flags and malformed options use parser error behavior.
- Stub randomness where deterministic output is required by a test.

### Verification commands

```text
python -m pytest -q
ruff check .
bandit -c pyproject.toml -r knockknock
pip-audit
```

Tooling that is not installed locally should be reported as unavailable rather
than treated as an application failure; CI remains the authoritative full
verification environment.

## 9. Delivery plan

1. **Contract:** Keep this specification, README usage, and public API names
   aligned.
2. **Implementation:** Maintain the three-layer boundary: catalogue/domain,
   sequence formatting, and CLI orchestration.
3. **Assurance:** Add or update unit and subprocess tests for every contract
   change, then run the project checks.
4. **Release review:** Confirm supported Python versions, package metadata,
   security scans, and clean-environment installation before publishing.

## 10. Future decisions

These are intentionally out of the initial delivery and require product
decisions before implementation:

- Whether deterministic random selection needs a user-facing seed option.
- Whether catalogue entries should carry stable IDs separate from display names.
- Whether output should support machine-readable JSON in addition to terminal
  text.
- Whether a coverage threshold or reproducible dependency constraints should
  become release gates.
- Whether publishing to a package index warrants signing and provenance
  requirements.
