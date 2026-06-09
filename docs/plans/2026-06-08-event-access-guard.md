# Event Access Guard

## Status: Completed

## Context

`EventHandler` calculated whether the current user owned the event and made a
Facebook friend visibility request for the event owner, but the callback rendered
`event.html` without enforcing either result. A logged-in user who knew an
`event_id` could reach event details without the owner/friend gate being applied.

## Objectives

- Preserve the existing event lookup and render flow for owners and visible
  friends.
- Reject non-owner, non-friend event access before rendering details.
- Keep the Facebook friend visibility check explicit.
- Cover the behavior in `make check`.

## Work Completed

- Added `_friendship_visible` to interpret Facebook friend-check responses.
- Returned HTTP 403 when the current user is not the event owner and the
  friend-check response is not visible.
- Extended `scripts/check_willbeout_contracts.py` with event access assertions.
- Updated README, VISION, and CHANGES with the access guard.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add runtime tests for event owner, friend, and non-friend access paths.
- Add a 404 guard for missing event IDs before reading event owner fields.
