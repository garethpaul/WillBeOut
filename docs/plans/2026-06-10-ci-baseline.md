# WillBeOut CI Baseline

## Status: Completed

## Context

`WillBeOut` has dependency-free Tornado handler contracts behind `make check`.
The repository needs a lightweight GitHub Actions gate so auth, event access,
request-id validation, metadata cleanup, and template integration guards run
before review.

## Objectives

- Run the existing contract checker in GitHub Actions.
- Keep the hosted runner job useful without requiring Python 2.
- Make the CI workflow presence part of the checked repository contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 in CI for the dependency-free contract checker.
- Guarded the legacy Python 2 syntax check so it runs when Python 2 is present
  and reports a clear skip otherwise.
- Extended `scripts/check_willbeout_contracts.py` to require the CI workflow
  and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check_willbeout_contracts.py`
- `git diff --check`

## Follow-Up Candidates

- Add a pinned Python 2 runtime job only if the project is intentionally revived
  with documented legacy dependencies.
