# Event Authorization Edge Matrix

Status: Completed

## Context

The modern no-network runtime suite already exercises denied access across the
protected event read and write endpoints. It checks ordinary queries and
mutations, but not `execute_transaction`, which is the write path used by the
availability endpoint. Missing-event behavior is executable only for one
message read even though every protected endpoint shares `require_event_access`.

## Changes

- Extend the protected-call assertion to include transactional writes.
- Exercise missing-event 404 behavior across every protected event read.
- Exercise missing-event 404 behavior across every protected event write.
- Require no Facebook friend lookup after the event lookup returns no row.
- Require no protected query, execute, rowcount, or transaction call.
- Keep production handlers and response semantics unchanged.

## Verification Plan

- Run the focused `EventEndpointAuthorizationTest` class.
- Temporarily remove one event-access call and prove the expanded matrix fails.
- Run `/usr/bin/make check` from checkout and an external working directory.
- Run Python compilation and `git diff --check`.
- Use hosted Python 3.10, 3.12, and 3.14 plus CodeQL as exact-head authority.

## Scope Boundaries

- No authentication, Facebook, database, handler, route, template, dependency,
  configuration, or response-body behavior change.
- Event creation and unscoped calendar routes remain outside the protected
  existing-event matrix.

## Verification Completed

- The focused authorization class passed 18 tests across owner, friend,
  forbidden, missing-event, validation, and mutation boundaries.
- A temporary mutation removed the message read access check; the new matrix
  failed with `404 != 200` for `/messages?event_id=1`.
- `/usr/bin/make check` passed from the checkout and through the absolute
  Makefile path from `/tmp` using the hash-locked virtual environment.
- The complete gate passed 31 static contracts, 40 no-network runtime tests, 31
  workflow mutations, 23 dependency-lock mutations, and 40 Make authority
  cases.
- `pip check`, `pip-audit -r requirements.lock`, Python compilation, and
  `git diff --check` passed with no known vulnerabilities.
