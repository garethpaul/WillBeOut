# Session Cookie Hardening

Status: Completed

## Context

The signed `user` cookie contains the Facebook user payload used by the legacy
application, including its access token. The cookie was signed but did not
explicitly prevent browser JavaScript access or transmission over plain HTTP.

## Changes

- Marked the signed user cookie `HttpOnly` and `Secure`.
- Added a static regression contract for both cookie attributes.
- Pinned CI to Ubuntu 24.04 with superseded-run cancellation.
- Made the verification Makefile independent of the caller's working directory.

## Verification

- `make check`
- Root-independent `make test`
- Mutation checks for cookie flags, CI, Make paths, and plan completion
- `git diff --check`
