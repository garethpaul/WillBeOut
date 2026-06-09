# Generated macOS Metadata

## Status: Completed

## Context

The repository still tracked `static/.DS_Store`, a local desktop metadata file
that can change without touching application behavior. Keeping generated
machine-local files in source control makes diffs noisier and weakens the
repository cleanup contract.

## Objectives

- Remove the tracked macOS metadata file.
- Ignore future `.DS_Store` files.
- Add a dependency-free static check that fails if `.DS_Store` files return.
- Keep the maintenance documentation aligned with the new cleanup contract.

## Work Completed

- Removed `static/.DS_Store` from the repository.
- Added `.DS_Store` to `.gitignore`.
- Added static checker coverage for generated macOS metadata.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make check`
- `git diff --check`
