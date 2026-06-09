# Message Id Validation

## Status: Completed

## Context

Vote, attendance, availability, and event-detail handlers already used the
shared `get_int_argument` helper, but message list, create, and delete flows
still read raw request arguments. Malformed message or event IDs could reach
database access or redirects before request validation failed.

## Objectives

- Validate delete-message IDs before database writes.
- Validate message event IDs before message queries and inserts.
- Preserve existing message create/list/delete flows for valid IDs.
- Keep redirects based on validated event IDs.
- Cover the message handlers in dependency-free static checks.

## Work Completed

- Updated delete-message handling to validate the `ide` and `event_id`
  arguments before deleting and redirecting.
- Updated message list handling to validate `event_id` before querying.
- Updated message create handling to validate the posted `id` event argument
  before insertion and redirect.
- Added static checker coverage for message ID validation.
- Updated README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
