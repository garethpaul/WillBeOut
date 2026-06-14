# Event Vote User Binding

Status: Completed

## Problem

The authorized desktop event page loads the current user's votes with
`int(_id)`, but `_id` is never defined in `EventHandler.get`. Owner and friend
requests can pass the shared access guard and then fail before rendering the
event page. Focused HTTP reproduction also showed that the modern Graph client
stores `id` and `name`, while the shared authenticated template still requires
the removed legacy `link` field and raises `KeyError` during rendering.
The same reproduction then reached a share-link expression that uses attribute
access on a plain PyMySQL `DictCursor` row and raises `AttributeError`.

## Requirements

1. Bind the authenticated user ID explicitly in the desktop event handler.
2. Pass that bound ID to the parameterized vote query after event access is
   authorized.
3. Build the authenticated profile link from the verified Graph user ID rather
   than requiring an unavailable session field.
4. Use dictionary access for the event share-link fields returned by the
   configured PyMySQL cursor.
5. Preserve the existing owner-or-friend access rule, event lookup, suggestion
   query, route, and successful response behavior.
6. Add a no-network runtime test that reaches the successful owner event page
   and proves the vote query receives the authenticated user ID.
7. Add mutation-sensitive static coverage for missing, undefined, or reordered
   user binding, incompatible template field access, and completed plan
   evidence.

## Verification Plan

- Reproduce the authorized event-page failure before implementation in an
  isolated environment created from `requirements.lock`.
- Run the focused runtime and static contracts, then local, external-directory,
  and hostile-root `make check` with explicit timeouts.
- Run dependency integrity and vulnerability audits.
- Inspect the exact diff, generated artifacts, structured files, whitespace,
  and changed lines for credential material.

## Scope Boundaries

- Do not alter event authorization, dependencies, routes, database schema, or
  unrelated legacy frontend assets.
- Do not merge or close stacked pull requests without explicit authorization.

## Work Completed

- Bound the authenticated user ID after event authorization and used it in the
  parameterized vote lookup.
- Replaced the unavailable legacy profile `link` field with an HTTPS profile
  URL derived from the verified Graph user ID.
- Replaced attribute-style event share fields with dictionary access compatible
  with the configured PyMySQL cursor.
- Added an owner-page HTTP regression and static contracts for the complete
  authorized render path.

## Verification Results

- Before implementation, the focused isolated HTTP reproduction returned 500
  with `NameError: _id is not defined`.
- The completed focused owner-page test returned 200 and confirmed the vote
  query received `(1, 42)`.
- All 22 no-network runtime tests and 22 implementation static contracts passed
  before enabling the completed-plan assertion.
- Six isolated hostile mutations were rejected: missing user binding, undefined
  vote user, pre-authorization binding, legacy Graph link dependence,
  attribute-style event access, and missing runtime parameter assertion.
- The workflow contract suite rejected all 18 hostile mutations.
- Local `make lint`, `make test`, `make contract-test`, `make build`, and
  `make check` passed 23 static contracts, 22 no-network runtime tests, and the
  18 workflow mutations under the exact five-package lock.
- External-directory and hostile-root `make check` gates passed with paths
  anchored to the protected Makefile root.
- `uv pip check` passed and `pip-audit==2.10.0` reported no known
  vulnerabilities in `requirements.lock`.
- A seventh focused mutation confirmed incomplete plan evidence is rejected.
