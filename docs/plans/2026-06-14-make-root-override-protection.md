# Make Root Override Protection

Status: Planned

## Problem

The Makefile derives an absolute repository root for source, checker, runtime
test, and cleanup paths, but its ordinary assignment can be replaced by a
command-line `ROOT` value. That permits verification to execute against or
delete generated artifacts from an unintended directory.

## Requirements

1. Protect the Makefile-derived repository root with GNU Make's `override`
   directive.
2. Preserve the configurable Python command and every existing verification
   target.
3. Require exact protected-root, tool-override, rooted-checker, rooted-runtime,
   and rooted-cleanup lines in the dependency-free checker.
4. Pass local, external-working-directory, and hostile-root full gates under
   the exact pinned dependency environment.
5. Reject focused mutations covering root derivation, cleanup scope, Python
   override semantics, checker paths, and completed-plan status.

## Verification

- Run Python compilation and the focused dependency-free contracts first.
- Run bounded local, external-working-directory, and hostile `ROOT` full
  `make check` gates.
- Run the exact dependency integrity and vulnerability audits.
- Run focused mutations and structured workflow/data-file checks.
- Inspect the exact diff and scan changed lines for credentials and generated
  artifacts before committing only intended paths.

## Scope Boundaries

- Do not change Python runtime behavior, dependencies, workflows, templates,
  vendored assets, public APIs, or deployment configuration.
- Do not merge or close any pull request without explicit owner authorization.
