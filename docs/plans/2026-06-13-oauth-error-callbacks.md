# OAuth Error Callbacks

Status: Completed

## Context

OAuth authorization servers return user denials and provider failures to the
registered callback with an `error` parameter and the original `state`. The
current login handler only distinguishes callbacks by the presence of a code,
so a valid error callback without a code starts a new authorization request.
That can trap a user who denies access in a redirect loop and leaves the
one-time OAuth cookies active.

RFC 6749 section 4.1.2.1 defines authorization-code error responses including
`access_denied` and requires the original state when the request included one.

## Requirements

- **R1:** Treat either `code` or `error` as an OAuth callback and require a
  valid constant-time state match before processing it.
- **R2:** Clear the transient OAuth state and destination cookies after a
  valid callback, including provider error callbacks.
- **R3:** Return a stable local 403 response for `access_denied` without
  restarting authorization or calling the token exchange.
- **R4:** Return a stable local 502 response for other provider errors without
  reflecting provider-controlled descriptions or calling the token exchange.
- **R5:** Reject ambiguous callbacks containing both `code` and `error`.
- **R6:** Preserve the existing successful authorization-code flow and safe
  destination handling.

## Implementation Units

### U1: Callback Classification And State Validation

**Goal:** Distinguish initial login requests from code/error callbacks while
keeping state validation ahead of every callback outcome.

**Files:** `auth.py`

**Test scenarios:**

- A request with neither code nor error starts authorization as before.
- An error callback with an invalid or missing state returns 400 before any
  provider exchange or error handling.
- A callback containing both code and error returns 400 after state validation.

### U2: Stable Provider Error Outcomes

**Goal:** Consume valid OAuth error callbacks locally, clear one-time cookies,
and avoid reflecting provider-controlled text.

**Files:** `auth.py`, `test_modern_runtime.py`

**Test scenarios:**

- A valid `access_denied` callback returns 403, clears transient cookies, and
  does not call Facebook authentication.
- A valid unknown/provider error returns 502 with stable local output and no
  provider description or token exchange.
- The existing successful state/code round trip still creates the encrypted
  session and redirects to the allowlisted destination.

### U3: Durable Contracts And Documentation

**Goal:** Make callback ordering, stable error behavior, completed-plan status,
and verification evidence part of the canonical gate.

**Files:** `scripts/check_willbeout_contracts.py`, `README.md`,
`docs/plans/2026-06-13-oauth-error-callbacks.md`

**Test scenarios:**

- Static contracts require error detection, state-before-error ordering,
  transient-cookie clearing, stable local statuses, and no use of
  `error_description`.
- Hostile mutations removing state validation, restarting authorization,
  exchanging a code on error, reflecting provider text, or retaining OAuth
  cookies fail focused or full verification.

## Scope Boundaries

- Keep Meta Graph endpoints, requested scopes, token storage, session cookies,
  safe-next allowlisting, and successful login behavior unchanged.
- Do not add provider-specific UI, retry loops, or persistence.
- Do not expose OAuth `error_description`, `error_uri`, authorization codes,
  access tokens, or provider response bodies.

## Verification

- All 6 focused `AuthHandlerTest` cases passed for successful login, invalid
  code/error state, denial, provider failure, and ambiguous callbacks.
- All 14 executable application tests, 21 static application contracts, and
  18 workflow mutations passed under the exact five-package Python 3.12 lock.
- Full `make check` passed from the repository and from an external working
  directory.
- Eight hostile mutations were rejected: restarting on error, bypassing state,
  disabling error handling, retaining OAuth cookies, reflecting provider text,
  logging callback queries, accepting code plus error, and restoring the
  caller-directory-dependent runtime test command.
- External verification exposed and fixed a pre-existing Makefile defect where
  runtime tests inherited the caller directory instead of running from the
  repository root.
- Python compilation and `git diff --check` passed.

## Source

- RFC 6749 section 4.1.2.1, Authorization Error Response:
  https://www.rfc-editor.org/rfc/rfc6749#section-4.1.2.1
