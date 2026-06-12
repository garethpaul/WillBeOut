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
- Disable checkout credential persistence and test workflow policy structurally.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Run the dependency-free contract checker on Python 3.10, 3.12, and 3.14.
- Pin actions to immutable revisions, grant only read access, bound jobs to five
  minutes, and retain manual dispatch for maintenance checks.
- Disable checkout credential persistence and add 17 dependency-free hostile
  mutations for credentials, permissions, triggers, actions, matrix coverage,
  runtime bounds, dependency installation, and the canonical gate.
- Guarded the legacy Python 2 syntax check so it runs when Python 2 is present
  and reports a clear skip otherwise.
- Extended `scripts/check_willbeout_contracts.py` to require the CI workflow
  and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python3 scripts/check_willbeout_contracts.py`
- `python3 -B scripts/test_workflow_contract.py`
- `git diff --check`

## Follow-Up Candidates

- Add a pinned Python 2 runtime job only if the project is intentionally revived
  with documented legacy dependencies.
