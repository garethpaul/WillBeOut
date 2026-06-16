# Availability Payload Validation

Status: Completed

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

- Restoring the original delete-before-parse sequence made the malformed
  payload regression fail because database writes occurred before the later
  token raised an error.
- The two focused handler tests passed: malformed and empty payloads returned
  HTTP 400 without writes, while `2,2,5` preserved duplicate values and issued
  the expected ordered replacement.
- All 26 no-network runtime tests passed under the exact supported dependency
  environment.
- Eight isolated hostile mutations were rejected across empty-token handling,
  integer conversion, parser invocation, runtime coverage, static registration,
  guidance, completed-plan status, and the original delete-before-parse flow.
- Repository and external-directory `make check` each passed 25 static
  contracts, 26 runtime tests, 21 workflow mutations, and 23 dependency-lock
  mutations under the supported exact dependency environment.
- Plan-aware correctness, security, testing, maintainability, and project
  standards review found no actionable issue.
- Exact eight-path diff, generated-artifact, secret-pattern, untracked-file,
  and whitespace audits passed before commit.
