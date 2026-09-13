# Interactive joke flow plan

1. Add an opt-in `--interactive` CLI mode while keeping the current five-line output as the default. Reuse the existing `Joke` catalogue and `tell()` data so selection and formatting stay unchanged.
2. Introduce a small interaction runner at the CLI boundary: print each caller line, read the expected response, then continue with the joke. Treat EOF and Ctrl-C as a clean, documented exit rather than a traceback.
3. Test the conversation with injected input/output (including the happy path, EOF, and interruption), and retain regression coverage for random, explicit, listing, and invalid-selector modes.
4. Document the new flag and example conversation in `README.md`, and update `DESIGN.md` if the interaction runner becomes a distinct presentation layer.
