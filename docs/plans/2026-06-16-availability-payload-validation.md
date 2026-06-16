# Availability Payload Validation

Status: Planned

## Problem

`TimeHandler.post` deletes the authenticated user's existing availability
before converting every submitted `availabletimes` token to an integer. A
payload such as `1,invalid` therefore commits the delete, commits the first
insert, and then fails while parsing the later token. Malformed input can erase
valid state and leave a partial replacement.

## Requirements

1. Decode and validate the complete comma-separated availability payload before
   issuing any DELETE or INSERT.
2. Return HTTP 400 for empty tokens or non-integer tokens without exposing the
   submitted value.
3. Preserve the existing authenticated event-access check before payload
   handling and preserve the successful redirect and database statement order.
4. Preserve the current representation: accepted integer tokens are inserted
   in submitted order and duplicate values remain accepted.
5. Add no-network runtime coverage proving malformed input performs no
   availability mutation and valid input still replaces the saved values.
6. Add mutation-sensitive static contracts for full-payload parsing,
   validation-before-delete ordering, runtime coverage, guidance, and completed
   plan evidence.

## Scope Boundaries

- Do not change the route, form field, templates, database schema, or event
  authorization policy.
- Do not add a multi-statement database transaction in this change; the defect
  is eliminated by completing all fallible payload conversion before writes.
- Do not merge or close the existing pull-request stack without explicit owner
  authorization.
- Do not weaken dependency, workflow, CodeQL, or lockfile verification.

## Implementation Units

### U1. Validate before mutation

- **Files:** `events.py`.
- Add a small parser that converts the complete decoded payload or raises the
  existing stable HTTP 400 boundary, then use its result before DELETE.

### U2. Add executable and portable coverage

- **Files:** `test_modern_runtime.py`, `scripts/check_willbeout_contracts.py`.
- Cover malformed later tokens, empty tokens, valid ordered replacement,
  database-call absence, parser use, operation ordering, and contract
  registration.

### U3. Preserve maintained guidance

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`.
- Record that availability replacement validates the complete payload before
  mutating persisted state.

## Verification

- Pending focused pre-fix reproduction and runtime tests.
- Pending repository and external-directory full gates.
- Pending isolated hostile mutations and exact diff, artifact, and secret
  audits.
