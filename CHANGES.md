# Changes

## 2026-06-21

- Isolated repository verification from caller-controlled Make startup files,
  shell state, execution modes, root overrides, Python expressions, and later
  public recipe replacement.
- Added adversarial Make authority coverage and bound hosted verification to
  `/usr/bin/make` without changing service behavior or dependencies.

## 2026-06-19

- Rejected non-ASCII OAuth callback state without raising an internal error.
- Preserved raw suggestion text for single-pass template autoescaping and
  rejected non-HTTP(S) suggestion links before storage.
- Removed inline event-name JavaScript from share links and isolated external
  suggestion links from their opener without double-loading the share handler.
- Restricted availability to unique rendered hours, allowed atomic clearing, and
  kept the submitted payload synchronized after client-side deselection.

## 2026-06-16

- Validated complete availability payloads before deleting or inserting saved times.
- Made availability replacement atomic on verified InnoDB storage.
- Updated the hash-locked Tornado runtime from 6.5.6 to 6.5.7 to remediate
  GHSA-pw6j-qg29-8w7f while preserving the reviewed resolved graph.
- Blocked cross-event vote creation and deletion by requiring each suggestion
  ID to belong to the already authorized event before vote storage is touched.

## 2026-06-15

- Added SHA-256 artifact hashes to the resolved production lock and made
  canonical pip installs fail closed with `--require-hashes`.
- Updated cryptography from 48.0.0 to 48.0.1 after the pinned audit identified
  GHSA-537c-gmf6-5ccf in the original exact pin.
- Added semantic lock contracts and hostile mutations for missing hashes,
  weak algorithms, dependency drift, marker loss, and unhashed workflow paths.

## 2026-06-14

- Fixed authorized desktop event pages to bind the authenticated user ID before
  loading that user's votes.
- Derived authenticated Facebook profile links from the verified user ID
  instead of requiring the unavailable legacy Graph `link` field.
- Made the event share action use dictionary access compatible with PyMySQL
  `DictCursor` rows.
- Added a no-network owner-page regression and mutation-sensitive static
  coverage for the parameterized vote lookup.

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
