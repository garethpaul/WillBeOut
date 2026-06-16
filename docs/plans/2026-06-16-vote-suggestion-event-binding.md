# Vote Suggestion Event Binding

Status: Completed

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
4. Join displayed vote totals by both suggestion ID and event ID so historical
   malformed rows cannot affect another event.
5. Preserve authenticated user binding, parameterized SQL, existing redirects,
   duplicate-vote behavior, and owner-or-friend event access.
6. Add no-network handler tests proving mismatches issue no vote query, insert,
   or delete and valid bindings preserve both mutation paths.
7. Add mutation-sensitive static contracts for both handlers, binding order,
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
  aggregate event scoping, contract registration, and plan completion.

### U4. Preserve maintained guidance

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`.
- Record the cross-event vote isolation boundary.

## Verification

- The cross-event handler test failed before implementation because `/vote`
  redirected and touched vote storage, then both create and delete returned 404
  without vote access after the exact-pair guard was added.
- Focused valid-binding tests preserved vote creation and removal redirects and
  mutations.
- Eight isolated hostile mutations were rejected across helper SQL, both
  handler calls, guard ordering, aggregate join scoping, runtime tests, static
  registration, and README guidance. The completed-plan mutation was rejected
  by the final full gate.
- Repository and external-directory `make check` passed the complete runtime,
  static, workflow, and hash-lock contract suites under Tornado 6.5.6.
- The configured package index did not expose locked `cryptography==48.0.1`, so
  a complete fresh `--require-hashes` install could not be repeated locally;
  lock semantics remained covered by the repository contract and canonical CI.
- Artifact, secret, dependency-drift, exact-diff, and whitespace audits are
  included in the final shipping gate.
