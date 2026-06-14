# Event Vote User Binding

Status: Planned

## Problem

The authorized desktop event page loads the current user's votes with
`int(_id)`, but `_id` is never defined in `EventHandler.get`. Owner and friend
requests can pass the shared access guard and then fail before rendering the
event page.

## Requirements

1. Bind the authenticated user ID explicitly in the desktop event handler.
2. Pass that bound ID to the parameterized vote query after event access is
   authorized.
3. Preserve the existing owner-or-friend access rule, event lookup, suggestion
   query, template context, route, and response behavior.
4. Add a no-network runtime test that reaches the successful owner event page
   and proves the vote query receives the authenticated user ID.
5. Add mutation-sensitive static coverage for missing, undefined, or reordered
   user binding and completed plan evidence.

## Verification Plan

- Reproduce the authorized event-page failure before implementation in an
  isolated environment created from `requirements.lock`.
- Run the focused runtime and static contracts, then local, external-directory,
  and hostile-root `make check` with explicit timeouts.
- Run dependency integrity and vulnerability audits.
- Inspect the exact diff, generated artifacts, structured files, whitespace,
  and changed lines for credential material.

## Scope Boundaries

- Do not alter event authorization, templates, dependencies, routes, database
  schema, or legacy frontend assets.
- Do not merge or close stacked pull requests without explicit authorization.
