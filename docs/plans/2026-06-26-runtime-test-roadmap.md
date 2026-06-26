# Runtime Test Roadmap Reconciliation

Status: completed

## Context

The no-network runtime suite now covers OAuth state and cookie handling, the
full protected-event access matrix, vote-to-event binding, and validated atomic
availability replacement. `VISION.md` still lists adding tests for those areas
as future work, which can misdirect maintenance toward already-completed work.

## Goals

- Replace the stale roadmap item with a maintained coverage invariant.
- Document the current runtime test inventory in the README.
- Make the static checker reject roadmap or coverage drift.
- Record the exact verification evidence for this documentation change.

## Work Completed

- Replaced the completed broad test priority with a maintained coverage invariant.
- Documented the four current no-network runtime coverage groups and test count.
- Added a static contract tied to representative executable tests.
- Required completed plan evidence so the roadmap cannot drift silently.

## Verification Completed

- `python3 scripts/check_willbeout_contracts.py` passed all 32 static contracts.
- `/usr/bin/make check` passed 32 static contracts, 40 executable no-network
  runtime tests, 31 workflow mutations, 23 dependency-lock mutations, and 40
  Make authority cases.
- Absolute-Makefile `/usr/bin/make check` passed from an external working directory.
- Five focused hostile mutations were rejected across README coverage, vision
  invariant, stale-priority removal, representative runtime tests, and plan status.
- `uv pip check --python .venv/bin/python` and
  `pip-audit -r requirements.lock` passed with no
  known vulnerabilities.
- Python compilation passed and bytecode cleanup left no generated cache files.
- `git diff --check` passed.
