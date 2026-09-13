# Architecture and security review

**Review date:** 2026-09-12  
**Scope:** The Python package and CLI under `knockknock/`, its tests, packaging metadata, documented design, dependency automation, CI workflow, and `CODEOWNERS`. This is a static review of the checkout plus the required local test run. The workspace does not contain Git metadata, repository settings, branch-protection configuration, dependency lockfiles, or a deployment environment, so those areas are assessed only from the files present.

## Evidence and conclusion

- `python3 -m pytest -q` completed successfully: **12 passed in 0.11s** (exit code 0).
- The application has no declared runtime dependencies (`pyproject.toml`), and the implementation is a small standard-library CLI with three coherent modules.
- CI runs tests, Ruff, Bandit, pip-audit, and Gitleaks. Third-party GitHub Actions are referenced by full commit SHA, and the workflow grants `contents: read`.
- No hard-coded credentials, private keys, or other material secrets were found in the reviewed source, tests, packaging, documentation, or workflow. The workflow's `GITHUB_TOKEN` reference is used only to support the Gitleaks action.

No material application security flaw is evidenced by this review. The findings below are primarily assurance gaps and hardening recommendations, not demonstrated exploits.

## Architecture and module boundaries

**Verified assessment — sound boundary, informational severity.** `jokes.py` owns the frozen `Joke` value object, immutable tuple catalogue, and lookup; `sequence.py` formats a joke into five lines; `__main__.py` owns argument parsing, selection, and output. This matches `DESIGN.md`, keeps data and presentation separate, and exposes a small package API from `__init__.py`. There is no network, filesystem, subprocess, deserialization, or dynamic-code boundary in application code.

**Recommendation — low.** If the catalogue grows or becomes externally managed, keep catalogue validation and lookup separate from terminal formatting and add an explicit service/use-case layer only when a real integration boundary appears. The current size does not justify additional abstraction.

## CLI input and error handling

**Verified assessment — low risk.** `argparse` handles option syntax and the mutually exclusive `--list`/`--joke` modes. A joke selector is either converted to an integer or treated as a name, and lookup rejects negative/out-of-range indexes and unknown names. User-facing lookup failures are converted to `parser.error`, producing a non-zero exit without a traceback. Output is generated only from the static catalogue, so selector text is not reflected into a shell command, path, format string, or HTML context.

**Recommendation — low.** Add tests for malformed options, both mutually exclusive options together, empty selectors, very large numeric selectors, and the CLI's exact exit/stderr contract. These cases are bounded by `argparse` and the in-memory catalogue today; the recommendation improves regression assurance rather than addressing an observed vulnerability.

## Dependencies and supply-chain posture

**Verified assessment — positive with an assurance gap, low severity.** There are no runtime dependencies. Build and optional development dependencies are declared in `pyproject.toml`; the optional tooling has bounded major-version ranges. Dependabot is configured for both pip and GitHub Actions. CI invokes `pip-audit`, Bandit, and Ruff, and all referenced actions are pinned to immutable-looking full SHAs with version comments.

**Verified finding — low: dependency resolution is not reproducible.** No lockfile or constraints file is present, and CI upgrades pip and resolves the package and optional tools at job time. This leaves builds dependent on the package index's current resolution and means a newly released transitive package can change CI behavior without a source change. No vulnerable package was demonstrated in this review; the local environment does not have `pip-audit` installed, although CI is configured to run it.

**Recommendation — low.** Add a documented, reviewed lock/constraints strategy for CI and release builds, retain hashes where practical, and make audit output part of the release evidence. Pinning every development package by hash is optional for this small project but would further reduce resolution drift.

## CI and branch protections

**Verified assessment — positive workflow controls, medium assurance gap.** Pull requests and pushes to `main` run test, quality, and security jobs; Python 3.9 and 3.12 are covered. Workflow permissions are restricted to `contents: read`. `CODEOWNERS` assigns the named owner to repository-wide, automation, packaging, and ownership-control paths.

**Verified finding — medium: branch protection is not evidenced.** `CODEOWNERS` expresses review ownership but does not itself require approval, require status checks, prevent force pushes, or restrict who can merge. No Git metadata or hosted-repository settings are available in this workspace, so the existence of those protections cannot be verified. This is a governance/control assurance gap, not evidence that the controls are absent.

**Recommendation — medium.** In the hosting service, require pull requests and CODEOWNER approval for `main`, require the test/quality/security checks, prohibit force pushes and deletion, and restrict bypass permissions. Record the settings or an export in the operational control evidence rather than relying on this checkout.

**Recommendation — low.** Pin the `pip install --upgrade pip` toolchain step to a reviewed version or otherwise document the accepted bootstrap risk. The action itself runs in GitHub-hosted infrastructure and does not receive repository write permission.

## Secrets exposure

**Verified assessment — no material finding.** Source and workflow review found no hard-coded credentials, private keys, or application secrets. The only secret reference is the platform-provided `GITHUB_TOKEN` passed to Gitleaks. The workflow's top-level permission is read-only for repository contents, and the application has no code path that reads environment secrets or sends data externally.

**Recommendation — low.** Keep secret scanning enabled on pull requests and protect any future release credentials with environment approvals, least-privilege permissions, and rotation procedures. Review generated build artifacts before publishing if the project later adds release automation.

## Test coverage and quality

**Verified assessment — good basic coverage, low assurance gap.** The 12 passing tests cover catalogue shape and uniqueness, case-insensitive/name and index lookup, invalid selectors, sequence formatting, random/default CLI behavior, listing, valid selection, and invalid CLI selection. Ruff is configured in CI, and the security workflow includes Bandit and pip-audit.

**Verified finding — low: no coverage measurement or minimum is configured.** The project has no coverage configuration or CI coverage threshold. The existing tests exercise the main paths, but the repository cannot demonstrate a quantitative coverage baseline or prevent future untested branches from being added.

**Recommendation — low.** Add coverage reporting and a modest enforced threshold, then expand tests around parser error paths and public API edge cases. Consider mutation testing only if the catalogue/lookup logic becomes business-critical.

## Deferred risks

These are not current findings in the reviewed application, but should be revisited if scope changes:

- If jokes become user- or network-supplied, validate and bound text at ingestion and review terminal/control-character handling before printing it.
- If the CLI reads files, invokes external programs, or adds network integrations, reassess path/command injection, SSRF, timeouts, and outbound-data policy; none of those surfaces exists now.
- If publishing packages is introduced, add trusted publishing or tightly scoped release credentials, artifact signing/provenance, and a protected release workflow.
- Reassess Python-version support and dependency pins when Python 3.9 leaves support or when CI adds more platforms.

## Prioritized remediation backlog

1. **Medium — verify and enforce `main` branch protections:** require PR review/CODEOWNER approval and all security-relevant CI checks; disable force-push/delete and limit bypasses. This closes the largest unverified control gap.
2. **Low — make CI dependency resolution reproducible:** adopt reviewed constraints/lockfiles and a documented update process, with hashes where practical.
3. **Low — add coverage reporting and a minimum threshold:** preserve the current behavior while making test assurance measurable.
4. **Low — extend CLI contract tests:** cover malformed and conflicting arguments, empty/large selectors, and stable error behavior.
5. **Low — document or pin bootstrap tooling:** address the unpinned pip upgrade and capture audit results as release evidence.
