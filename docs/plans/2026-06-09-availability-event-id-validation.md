# Availability Event Id Validation

status: completed

## Context

The event detail, vote, and attendee handlers now use the shared integer
request helper, but `TimeHandler` still reads availability `event_id` values as
raw request arguments. Invalid ids can reach inline casts in the database
read/write paths instead of returning the same clear malformed-request response
as the guarded event and vote routes.

## Completed Scope

- Preserve existing availability update and JSON read behavior for valid ids.
- Updated `TimeHandler.post` and `TimeHandler.get` to call
  `get_int_argument('event_id')`.
- Used the validated integer in availability delete, insert, and query calls.
- Redirected availability updates with a stringified validated event id.
- Extended `scripts/check_willbeout_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `python2 -m py_compile __init__.py attendees.py auth.py base.py cal.py events.py facebook.py ismobile.py messages.py mobile.py prettydate.py votes.py`
- `make check`
- `git diff --check`

## Follow-Up Candidates

- Apply integer argument validation to message and calendar handlers.
- Validate individual availability time slots before inserts.
