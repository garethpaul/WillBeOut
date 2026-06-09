# Desktop Event Missing Guard

## Status: Completed

## Context

The mobile event handler returned 404 when an event id did not resolve, but the
desktop event handler continued into suggestion queries and owner-field access.
A missing or stale event id could therefore raise an internal error instead of
returning a clear not-found response.

## Objectives

- Preserve the desktop event owner/friend access flow.
- Return 404 when the event lookup does not find a record.
- Stop before related suggestion queries or owner-field access on missing
  events.
- Keep static checks covering desktop and mobile event access behavior.

## Work Completed

- Added a missing-event check immediately after the desktop event lookup.
- Raised `tornado.web.HTTPError(404)` before suggestion queries and owner
  checks.
- Extended the static checker and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add runtime tests for denied and missing event access.
- Validate event id arguments before integer conversion.
