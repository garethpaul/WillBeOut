# Safe Auth Next Redirect Plan

Date: 2026-06-08

Status: Completed

## Goal

Prevent Facebook login callbacks from redirecting to external URLs supplied in
the `next` query parameter.

## Scope

- Add a `BaseHandler` helper that accepts only site-local absolute paths.
- Reject protocol-relative `//host` redirects and fall back to `/events`.
- Use the sanitized `next` path when building the Facebook login callback URL.
- Use the sanitized `next` path when redirecting after authentication.
- Add dependency-free static checks for the auth redirect contract.

## TDD Notes

- Red: `python3 scripts/check_willbeout_contracts.py` failed with
  `AssertionError: BaseHandler must expose a safe next-url helper`.
- Green: `python3 scripts/check_willbeout_contracts.py` passed after adding the
  helper and routing the auth callback through it.

## Verification

- `python3 scripts/check_willbeout_contracts.py`
- `make check`
- `git diff --check`
