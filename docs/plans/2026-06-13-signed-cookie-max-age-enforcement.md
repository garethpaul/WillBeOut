# Signed Cookie Max-Age Enforcement

Status: Completed

## Problem

The application sets the encrypted user cookie to expire after one day and the
OAuth state/next cookies after ten minutes, but reads each with Tornado's
default signed-cookie verification age of 31 days. A manually replayed cookie
can therefore remain server-valid after its intended browser expiry.

## Requirements

1. Verify the user cookie with the same one-day maximum age used when setting it.
2. Verify OAuth state and next cookies with the same ten-minute maximum age used
   when setting them.
3. Keep cookie names, Secure/HttpOnly/SameSite attributes, encrypted token
   storage, OAuth state comparison, callback errors, and redirect allowlists
   unchanged.
4. Add no-network runtime tests proving fresh signed cookies are accepted and
   cookies older than each boundary are rejected without token exchange.
5. Add dependency-free contracts and hostile mutations for missing, swapped,
   or weakened server-side age limits.

## Verification

- Run focused session and OAuth cookie-age runtime tests under the exact lock.
- Run hostile static and runtime mutations for both lifetime boundaries.
- Run local and external-working-directory `make check` with explicit timeouts.
- Inspect the exact diff and scan changed lines for credentials and artifacts.

## Scope Boundaries

- Do not change cookie payloads, rotate deployment secrets, add refresh tokens,
  alter provider scopes, or broaden redirect destinations.
- Do not merge or close any pull request without explicit owner authorization.

## Verification Results

- The fresh OAuth round trip passed, while an eleven-minute OAuth state cookie
  and a two-day user cookie were rejected; the expired callback made no token
  exchange.
- Before this status update, the dependency-free checker reached only the
  required plan-completion assertion after all implementation contracts passed.
- Six isolated mutations were rejected for expanded user or OAuth ages, missing
  user/state/next read limits, and stale plan status.
- Local and external-working-directory `timeout 300s make check` passed 22
  static contracts, 21 no-network runtime tests, and 18 workflow mutations
  under the exact pinned environment.
