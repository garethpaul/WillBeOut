# Cookie Secret Contract Plan

Date: 2026-06-08

status: completed

## Goal

Make WillBeOut safer to inspect and run by removing the hardcoded Tornado
secure-cookie signing secret and fixing a syntax artifact in the auth handler.

## Scope

- Read Tornado `cookie_secret` from `COOKIE_SECRET` deployment configuration.
- Remove the stray non-code suffix from `auth.py`.
- Add static contracts for cookie-secret configuration and auth syntax hygiene.
- Add local verification targets that do not require the legacy runtime services.
- Ignore and clean generated Python bytecode created during local checks.

## TDD Notes

- Red: `python3 scripts/check_willbeout_contracts.py` failed with `AssertionError: facebook.py must read COOKIE_SECRET from configuration`.
- Green: `python3 scripts/check_willbeout_contracts.py` passed after moving `cookie_secret` to configuration and removing the auth suffix.

## Verification

- `make lint`
- `make test`
- `make verify`
- `make check`
- `python3 scripts/check_willbeout_contracts.py`
- `python2 -m py_compile __init__.py attendees.py auth.py base.py cal.py events.py facebook.py ismobile.py messages.py mobile.py prettydate.py votes.py`
- `git diff --check`

Full runtime verification still requires a Python 2 compatible environment for
the legacy Tornado and MySQL dependencies.
