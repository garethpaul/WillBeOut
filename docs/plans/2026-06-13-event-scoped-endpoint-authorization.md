# Event-Scoped Endpoint Authorization

Status: Completed

## Problem

Desktop and mobile event pages enforce the owner-or-Facebook-friend access
rule, but their supporting attendee, message, vote, suggestion, and
availability endpoints trust any authenticated caller-supplied event ID. A
signed-in user can therefore read or mutate event-scoped data without first
passing the event access decision used by the page itself.

## Requirements

1. Centralize event lookup and owner-or-friend authorization in `BaseHandler`.
2. Return 404 for missing events and 403 for existing events outside the
   caller's authorized Facebook relationship.
3. Reuse the shared authorization in desktop and mobile event-page handlers.
4. Authorize before database reads or writes in attendee, message, vote,
   suggestion, and availability handlers.
5. Keep authentication, integer argument validation, XSRF protection,
   parameterized SQL, and successful redirects unchanged.
6. Add runtime tests proving unauthorized requests do not reach protected data
   queries or mutations, plus mutation-sensitive static contracts covering
   every event-scoped handler method.

## Compatibility Boundary

- Preserve the existing access model: an event is visible to its owner or a
  caller present in the owner's Facebook-friend result set.
- Preserve public routes, request argument names, response formats, templates,
  and successful owner/friend workflows.
- Do not broaden event access to arbitrary authenticated users or infer access
  from attacker-controlled attendee, vote, or message rows.
- Do not log access tokens, Facebook response data, query strings, or private
  event content while denying access.

## Work Completed

- Added a shared `BaseHandler.require_event_access` guard that returns missing
  events as 404, accepts owners without a Graph call, and requires an exact
  Facebook friend ID match for other callers.
- Reused the shared guard in desktop and mobile event pages before related data
  queries.
- Guarded every attendee, message, vote, suggestion, and availability read or
  write before protected database access.
- Bound message deletion to the authorized event ID as well as the message and
  current user.
- Added executable HTTP coverage for denied reads and writes, owner and friend
  success paths, missing events, and no protected database access after denial.
- Added static contracts that enumerate every guarded handler method and retain
  the runtime assertions.

## Verification

- `make check` passed 22 static contracts, 19 no-network runtime tests, and 18
  workflow mutations under the exact five-package lock on Python 3.12.
- The same complete gate passed when invoked from `/tmp` through the
  repository-rooted Makefile.
- Nine hostile mutations were rejected: central 403 bypass, one removed guard
  from each of six handler groups, message deletion escaping the authorized
  event, and regressed plan completion status.
- Plan-aware security, correctness, testing, and maintainability review found
  no actionable findings after correcting the ID-validation wording.
- `git diff --check` passed for the completed implementation.
