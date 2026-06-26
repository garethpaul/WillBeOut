---
status: completed
---

# Document Project Status and Setup

## Problem

The README already contained a reproducible Python environment bootstrap,
configuration inventory, and local entry point, but it did not state whether
the repository or hosted service should be treated as active. The roadmap still
listed both setup notes and archive status as future work.

## Decision

- Describe WillBeOut as a maintained historical application with bounded
  security, dependency, compatibility, and documentation work.
- Record the GitHub repository's current unarchived state without claiming that
  the original hosted service is currently operated or supported.
- Point readers to the existing credentialed setup requirements and no-network
  verification path rather than inventing a public deployment promise.
- Remove the completed README setup/status item from future priorities.

## Verification

- Observed the static contract fail on the missing `## Project Status` section.
- `python3 scripts/check_willbeout_contracts.py`
- Installed `requirements.lock` with hashes into an isolated virtual environment
  and passed `make check`: 31 static contracts, 39 no-network runtime tests, 31
  workflow mutations, 23 dependency-lock mutations, and 40 Make authority cases.
- `python -m pip check`
- `pip-audit -r requirements.lock` reported no known vulnerabilities.
- `git diff --check`
- Three isolated hostile mutations were rejected: deleting the status section,
  restoring the completed roadmap item, and removing `make check` evidence from
  this plan.
