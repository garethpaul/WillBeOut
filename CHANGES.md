# Changes

## 2026-06-09

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
