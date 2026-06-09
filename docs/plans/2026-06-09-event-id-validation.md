# Event Id Validation

## Status: Completed

## Context

The desktop and mobile event pages accepted event id request arguments and
converted them inline with `int(...)` while preparing database queries. A
missing argument already receives Tornado's request error, but malformed ids
could raise a raw conversion exception instead of a clear client error.

## Objectives

- Preserve the existing desktop and mobile event access checks.
- Validate event id route arguments before database queries.
- Return HTTP 400 for malformed event ids.
- Keep the missing-event 404 and owner/friend 403 checks unchanged.

## Work Completed

- Added `BaseHandler.get_int_argument` for shared integer request validation.
- Updated desktop event handling to use the validated `event_id`.
- Updated mobile event handling to use the validated `id`.
- Extended the static contract checker and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_willbeout_contracts.py`
- `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile scripts/check_willbeout_contracts.py`
- `python2 -m py_compile __init__.py attendees.py auth.py base.py cal.py events.py facebook.py ismobile.py messages.py mobile.py prettydate.py votes.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Apply integer argument validation to vote, attendance, message, and calendar
  handlers.
- Add runtime tests for malformed, missing, denied, and missing-record event
  requests.
