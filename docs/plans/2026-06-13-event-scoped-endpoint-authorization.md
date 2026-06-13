# Event-Scoped Endpoint Authorization

Status: Planned

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
5. Keep authentication, positive integer argument validation, XSRF protection,
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

## Verification

Pending implementation.
