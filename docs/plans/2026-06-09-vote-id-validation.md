# Vote Id Validation

## Status: Completed

## Context

The desktop and mobile event detail routes now validate event ids before
database queries, but the vote handlers still read `event_id` and suggestion
`id` directly from request arguments. Malformed ids could raise conversion
errors or reach delete/write statements without the shared request validation.

## Objectives

- Preserve existing vote and change-vote behavior for valid ids.
- Validate `event_id` before vote database writes and deletes.
- Validate suggestion `id` before vote database writes and deletes.
- Return HTTP 400 for malformed vote ids through the shared helper.
- Keep Python 2 syntax compatibility.

## Work Completed

- Updated `VoteHandler` to use `get_int_argument` for event and suggestion ids.
- Updated `ChangeVoteHandler` to use `get_int_argument` for event and
  suggestion ids.
- Removed re-casts of already validated request ids.
- Extended `scripts/check_willbeout_contracts.py` and completed-plan coverage.
- Updated README, VISION, and CHANGES.

## Verification

- Negative check: `python3 scripts/check_willbeout_contracts.py` failed before
  vote id validation was added.
- `python3 scripts/check_willbeout_contracts.py`
- `python2 -m py_compile __init__.py attendees.py auth.py base.py cal.py events.py facebook.py ismobile.py messages.py mobile.py prettydate.py votes.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Apply integer argument validation to attendance, message, and calendar
  handlers.
- Add runtime tests for malformed vote ids and denied event access.
