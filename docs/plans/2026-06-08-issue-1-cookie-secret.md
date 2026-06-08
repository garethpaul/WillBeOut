---
title: Issue 1 Cookie Secret Configuration
type: fix
status: active
date: 2026-06-08
origin: https://github.com/garethpaul/WillBeOut/issues/1
execution: code
---

# Issue 1 Cookie Secret Configuration

## Summary

Remove the public Tornado cookie signing secret from the application and require each deployment to provide its own `COOKIE_SECRET`.

## Problem Frame

Issue #1 was filed from the public repository security review because `facebook.py` hardcodes the `cookie_secret` used by Tornado secure cookies. `base.py` trusts the signed `user` cookie to identify authenticated users, so any deployment using the repository default could allow forged identities.

## Requirements

- R1. `facebook.py` must not contain the public hardcoded cookie secret.
- R2. The application must read the signing secret from deploy-time configuration.
- R3. Startup must fail closed when no cookie secret is configured.
- R4. README must document how to generate and export a strong `COOKIE_SECRET`.
- R5. The PR must reference `https://github.com/garethpaul/WillBeOut/issues/1` and be marked `URGENT`.

## Implementation Unit

### U1. Deploy-Time Cookie Secret

- **Goal:** Add a validated `cookie_secret` option backed by the `COOKIE_SECRET` environment variable, use it in Tornado settings, and document setup for deployers.
- **Files:** `facebook.py`, `README`, `scripts/check-cookie-secret.sh`
- **Test Scenarios:** Verify the old public secret is gone, `COOKIE_SECRET` is required, README documents setup, and `facebook.py` still parses as Python source.
- **Verification:** `scripts/check-cookie-secret.sh`, `python3 -m py_compile facebook.py`, and `git diff --check`.

## Risks

- Existing deployments must set `COOKIE_SECRET` before restart.
- Changing the signing secret invalidates existing login cookies, requiring users to sign in again.
