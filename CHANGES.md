# Changes

## 2026-06-13

- Enforced the documented one-day user session and ten-minute OAuth cookie
  lifetimes during server-side signed-cookie verification.
- Centralized owner-or-Facebook-friend authorization and applied it before all
  event-scoped attendee, message, vote, suggestion, and availability access.

## 2026-06-12

- Migrated first-party modules from Python 2 syntax and removed Tornado APIs
  deleted before Tornado 6.
- Replaced the vulnerable legacy requirement set with exact Tornado 6.5.6,
  PyMySQL 1.2.0, and cryptography 48.0.0 pins plus a five-package lock.
- Replaced `tornado.database` with a parameterized PyMySQL adapter that rolls
  back failed writes and closes every connection.
- Replaced the removed Facebook mixin with an explicit Graph API v24.0 client,
  configured HTTPS callback, OAuth state binding, bounded responses, and
  redacted errors.
- Encrypted Facebook access tokens before signed-cookie storage and enabled
  template autoescaping with explicit raw XSRF form markup.
- Added executable no-network runtime tests and a resolved dependency-audit
  job while preserving the existing first-party security contracts.

- Restricted authentication return paths to literal `/` and `/events`
  destinations and removed the redundant high-cost mobile user-agent regex.
- Added reviewed SRI and anonymous CORS attributes to fixed-version jQuery and
  jQuery Mobile resources.
- Added immutable-pinned CodeQL analysis for actions, Python, and first-party
  JavaScript, with an exact checksum guard around the sole vendored Bootstrap
  exclusion.
- Removed the unused duplicate minified Bootstrap bundle and expanded
  `make check` contracts for the security and analysis scope.

## 2026-06-10

- Enabled Tornado XSRF enforcement, converted attendance, voting, message
  deletion, and logout mutations from GET to POST, and added tokens to native
  forms and all same-origin AJAX writes.
- Added a pinned, read-only GitHub Actions workflow that runs `make check` on
  Python 3.10, 3.12, and 3.14 for the dependency-free Tornado handler contract
  baseline with credential-free checkout.
- Added dependency-free workflow tests that reject contradictory credentials,
  write permissions, unreviewed actions, and weakened CI commands.
- Guarded the legacy Python 2 syntax step so hosted CI can run the baseline
  when Python 2 is unavailable.
- Replaced active template-side jQuery, Facebook, Yelp, and share/profile HTTP
  integrations with HTTPS and added static coverage.
- Marked the signed Facebook user cookie `HttpOnly` and `Secure` so the browser
  does not expose it to JavaScript or send it over plain HTTP.
- Pinned hosted verification to Ubuntu 24.04 with superseded-run cancellation
  and made Make targets independent of the caller's working directory.

## 2026-06-09

- Removed tracked macOS metadata and added static checker coverage to keep it
  out of source control.
- Added shared integer request validation for message event ids and
  delete-message ids.
- Added static checker coverage for malformed message id handling.
- Added shared integer request validation for attendance event ids.
- Added static checker coverage for malformed attendance event id handling.
- Added shared integer request validation for availability event ids.
- Added static checker coverage for malformed availability event id handling.
- Added shared integer request validation for desktop and mobile event ids.
- Added static checker coverage for malformed event id handling.
- Added shared integer request validation for vote and change-vote ids.
- Added static checker coverage for malformed vote id handling.
- Returned 404 for missing desktop events before reading owner fields or
  querying related suggestions.
- Added static checker coverage for the desktop missing-event guard.
- Enforced owner/friend access before rendering mobile event details and
  returned 404 for missing mobile events.
- Added static checker coverage for the mobile event access contract.

## 2026-06-08

- Enforced event owner/friend access before rendering event details.
- Restricted Facebook login `next` redirects to local absolute paths.
- Standardized docs-plan completion status while preserving `make check`
  evidence enforcement.
- Removed a stray non-code suffix from the Facebook auth redirect path.
- Added static contracts for the configured Tornado cookie secret.
- Added `make verify`/`make check` verification and Python 2 syntax checks.
