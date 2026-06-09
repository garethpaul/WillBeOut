# Mobile Event Access Guard

## Status: Completed

## Context

The desktop event route enforces owner-or-friend access before rendering event
details, but the mobile event route still rendered `mobile_event.html` directly
after loading an event by ID. Authenticated users should not be able to bypass
event visibility by using the mobile route.

## Objectives

- Preserve the mobile event detail flow for event owners and Facebook friends.
- Return 404 when the requested event does not exist.
- Reuse the owner-or-friend access model from the desktop event route.
- Enforce access before rendering `mobile_event.html`.
- Keep static checks covering the mobile event access contract.

## Work Completed

- Loaded mobile event and place query results into handler state before the
  asynchronous Facebook friend check.
- Returned `HTTPError(404)` for missing events.
- Added mobile `_friendship_visible` handling and a `_go` callback.
- Returned `HTTPError(403)` for non-owner, non-friend mobile event access.
- Extended `scripts/check_willbeout_contracts.py` and updated README, VISION,
  and CHANGES.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Validate event IDs before integer conversion in route handlers.
- Replace debug `print` statements with structured, non-sensitive logging.
