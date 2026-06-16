# Vote Suggestion Event Binding

Status: Planned

## Problem

Vote handlers authorize the supplied event but do not verify that the supplied
suggestion belongs to that event. An attendee of one event can submit a global
suggestion ID from another event and create or delete a cross-event vote row.
The event-page aggregate joins votes by suggestion ID, so the malformed row can
affect another event's displayed total.

## Requirements

1. Require an exact `(suggestion_id, event_id)` match after event access is
   authorized and before any vote read or write.
2. Return HTTP 404 for a missing or mismatched suggestion without disclosing
   another event's suggestion membership.
3. Apply the same binding to vote creation and vote removal.
4. Preserve authenticated user binding, parameterized SQL, existing redirects,
   duplicate-vote behavior, and owner-or-friend event access.
5. Add no-network handler tests proving mismatches issue no vote query, insert,
   or delete and valid bindings preserve both mutation paths.
6. Add mutation-sensitive static contracts for both handlers, binding order,
   exact SQL parameters, tests, guidance, and completed-plan evidence.

## Scope Boundaries

- Do not change database schema, aggregation order, routes, templates, or UI.
- Do not merge or close the existing pull-request stack without explicit owner
  authorization.
- Do not weaken the hash-verified dependency or hosted security gates.

## Implementation Units

### U1. Add shared suggestion binding

- **Files:** `base.py`.
- Add a fail-closed helper that looks up a suggestion by both ID and event ID.

### U2. Guard both vote mutations

- **Files:** `votes.py`.
- Invoke the binding helper after event access and before vote database work.

### U3. Add executable and portable coverage

- **Files:** `test_modern_runtime.py`, `scripts/check_willbeout_contracts.py`.
- Cover invalid create/delete, valid create/delete, SQL parameters, ordering,
  contract registration, and plan completion.

### U4. Preserve maintained guidance

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`.
- Record the cross-event vote isolation boundary.

## Verification

- Pending implementation.
- Run focused handler tests first, then the full pinned `make check` from the
  repository and an external directory.
- Run isolated hostile mutations across helper SQL, both handler calls,
  ordering, tests, guidance, and completed-plan status.
- Audit artifacts, secrets, dependency drift, exact diff, and whitespace before
  the explicit-path commit.
