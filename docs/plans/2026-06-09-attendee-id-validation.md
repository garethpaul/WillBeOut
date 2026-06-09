# Attendee Id Validation

status: completed

## Context

The event detail and vote handlers already reject malformed integer ids before
database access, but the attendance endpoints still accepted raw `event_id`
values or escaped strings. Escaping does not prove the value is an event id and
leaves malformed requests to reach attendance queries and writes.

## Completed Scope

- Updated attend, unattend, and attendance-data handlers to use the shared
  integer request helper for `event_id`.
- Removed the unused `re.escape` import from `attendees.py`.
- Redirected attendance writes with the validated integer id string.
- Extended the static contract checker to keep attendance handlers on the
  shared id-validation path.

## Verification

- `make check`
- `git diff --check`
