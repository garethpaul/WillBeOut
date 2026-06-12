# Modern Python Web Runtime

status: planned

## Context

The application is a Python 2-era Tornado/Facebook/MySQL sample whose direct
manifest currently exposes fourteen GitHub Dependabot alerts: nine Tornado
advisories, three Gunicorn advisories, one simplejson advisory, and one older
Tornado advisory duplicated across the current vulnerable range. The secure
floors are Tornado 6.5.5, Gunicorn 22.0.0, and simplejson 2.6.1.

This is not a safe pin-only update. Tornado 6 removed `tornado.database`, the
`@tornado.web.asynchronous` callback lifecycle, and the legacy
`FacebookGraphMixin` integration used throughout the application. The source
also contains Python 2 print statements and `urllib` APIs, while the manifest
contains obsolete Python 2-only packages such as MySQL-python and wsgiref.

## Priority

Eliminate the known direct-dependency exposure by migrating first-party code
to a supported Python 3 and Tornado runtime with executable no-network tests.
Do not claim advisory remediation until the application imports, starts with
injected fakes, and preserves its existing authorization and XSRF contracts.

## Prioritized Work

1. Establish Python 3.12 syntax, exact modern direct pins, a resolved lock, and
   a dependency audit without weakening the existing static security gates.
2. Replace `tornado.database` with a narrow injected database interface backed
   by a maintained MySQL driver and preserve parameterized query behavior.
3. Replace callback-only Tornado handlers and removed asynchronous decorators
   with supported synchronous or `async def` request lifecycles.
4. Replace the removed Facebook mixin with a bounded explicit Graph client and
   OAuth flow that validates state, redirect targets, response types, timeouts,
   and error handling without logging tokens or response bodies.
5. Add executable application/handler tests with fake database and Facebook
   clients before changing the deployment command or closing alerts.

## Requirements

- R1. Target Python 3.12 and pin Tornado 6.5.5 or newer, Gunicorn 22.0.0 or
  newer, and maintained direct dependencies exactly; remove unused or
  standard-library packages from runtime requirements.
- R2. Commit an exact resolved production lock and require `pip check` plus a
  pinned `pip-audit` job to report zero known vulnerabilities.
- R3. Make every first-party Python module compile and import on Python 3.12
  without credentials or network access.
- R4. Replace `tornado.database` and MySQL-python with an injected database
  boundary whose real adapter uses parameterized operations and closes
  connections predictably.
- R5. Remove `@tornado.web.asynchronous`, Python 2 print statements, and Python
  2 `urllib` calls while preserving request completion and redirect behavior.
- R6. Replace `FacebookGraphMixin` with an explicit client. OAuth state must be
  bound to the secure session, next redirects must remain local-only, HTTP
  calls must use HTTPS with bounded timeouts, and tokens or payloads must not
  appear in errors or logs.
- R7. Preserve secure, HTTP-only session cookies, XSRF protection for writes,
  integer ID validation, owner/friend access checks, HTTPS integrations, and
  the existing first-party CodeQL exclusions.
- R8. Add dependency-injected no-network tests for application startup,
  authentication decisions, Graph failures, database queries/writes, route
  methods, XSRF behavior, and error redaction.
- R9. Update README, security, vision, changes, contributor guidance, and this
  plan with actual completed work and exact local/hosted evidence.

## Scope Boundaries

- Do not contact Facebook/Meta, MySQL, or any deployed environment from local
  or hosted verification.
- Do not preserve removed Tornado APIs through local compatibility shims that
  merely hide an untested migration.
- Do not merge or close pull requests #2, #4, or #6 without explicit owner
  authorization.
- Do not weaken the current static first-party security checker or CodeQL
  exclusion boundary.

## Verification

- all first-party modules compile and import under Python 3.12
- focused fake-client application and handler tests
- `make lint`, `make test`, `make build`, and `make check`
- clean lock install, `pip check`, and zero-vulnerability dependency audit
- hostile mutations for legacy pins/APIs, unsafe OAuth state, nonlocal
  redirects, unbounded HTTP, raw token errors, SQL interpolation, XSRF bypass,
  and weakened static evidence
- `git diff --check`
- successful exact-head push, pull-request, dependency-audit, and CodeQL runs
