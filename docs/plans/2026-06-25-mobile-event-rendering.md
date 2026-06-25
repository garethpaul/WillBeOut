# Mobile Event Rendering

## Status: Completed

## Context

The modern database adapter returns dictionaries through PyMySQL `DictCursor`,
but the authorized mobile event template still used legacy attribute access.
As a result, valid mobile event requests failed during template rendering. The
mobile suggestion query also counted votes without requiring the vote row to
belong to the same event as the suggestion, unlike the desktop query.

## Objectives

- Render authorized mobile events from `DictCursor` rows.
- Preserve the existing owner-or-friend authorization guard.
- Count only votes bound to the requested event.
- Add runtime and static regression coverage.

## Work Completed

- Replaced legacy event and suggestion attribute access in
  `templates/mobile_event.html` with dictionary access.
- Added the event-ID equality constraint to the mobile vote join.
- Added an authorized mobile event runtime test that exercises rendering and
  verifies the event-bound query.
- Extended the static contracts and change log for the corrected behavior.

## Verification

- `.venv/bin/python -m unittest test_modern_runtime.EventEndpointAuthorizationTest.test_owner_mobile_event_page_binds_votes_to_the_requested_event`
- `make check` with `PYTHON=.venv/bin/python`
- `git diff --check`

## Follow-Up Candidates

- Replace the retired client-side Yelp JSONP integration with a supported,
  server-mediated place search.
- Add explicit message length and blank-message validation.
