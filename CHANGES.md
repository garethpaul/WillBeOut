# Changes

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
