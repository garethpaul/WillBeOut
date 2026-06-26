# WillBeOut

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

WillBeOut is a Tornado event-coordination application with Meta login and
MySQL persistence. The maintained runtime targets Python 3.10 or newer,
Tornado 6.5.7, PyMySQL 1.2.0, and an explicit Meta Graph API v24.0 boundary.

The repository keeps live services outside automated tests. Fake database,
HTTP, Graph, and session dependencies exercise the runtime without credentials
or network access.

## Project Status

WillBeOut is a maintained historical application. The repository receives
bounded security, dependency, compatibility, and documentation work rather
than feature commitments or hosted-service support. As verified on June 25,
2026, the GitHub repository is not archived.

Repository maintenance does not confirm that willbeout.com is currently operated.
Running the full application requires an isolated Meta app, a registered HTTPS
redirect URI, a MySQL database, and deployment secrets described below. The
credential-free `make check` path is the supported way to validate a checkout
without those services.

## Repository Contents

- `facebook.py` - application entry point and route configuration
- `database.py` - parameterized PyMySQL adapter
- `facebook_client.py` - bounded HTTPS OAuth and Graph client
- `session.py` - Fernet encryption for browser-session authentication data
- `test_modern_runtime.py` - executable no-network runtime tests
- `scripts/` - static and workflow mutation contracts
- `requirements.txt` - exact direct dependency pins
- `requirements.lock` - exact resolved production graph
- `templates/` and `static/` - server-rendered UI and local assets
- `docs/plans/` - completed and active engineering plans

## Getting Started

### Prerequisites

- Git
- Python 3.10 or newer

### Setup

```bash
git clone https://github.com/garethpaul/WillBeOut.git
cd WillBeOut
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements.lock
```

The exact graph should pass:

```bash
python -m pip check
pip-audit -r requirements.lock
```

After a reviewed direct dependency change, regenerate the universal hash lock:

```bash
uv pip compile requirements.txt --generate-hashes --universal --python-version 3.10 --output-file requirements.lock
```

## Configuration

Required production values:

- `COOKIE_SECRET` signs Tornado cookies.
- `SESSION_ENCRYPTION_KEY` encrypts Meta access tokens before signed-cookie
  storage. Generate it with
  `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`.
- Signed user cookies are accepted server-side for at most one day; transient
  OAuth state and next cookies are accepted for at most ten minutes.
- `FACEBOOK_API_KEY` and `FACEBOOK_SECRET` identify the Meta application.
- `FACEBOOK_REDIRECT_URI` is the exact registered HTTPS callback ending in
  `/auth/login`; request Host headers are not used to construct it.
- `FACEBOOK_GRAPH_VERSION` defaults to the reviewed `v24.0` boundary.
- `MYSQL_HOST`, `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD` configure
  persistence.

Run locally after configuring an isolated Meta app and database:

```bash
python3 facebook.py --port=5000
```

The `Procfile` uses the same Python 3 entry point.

## Testing and Verification

- `/usr/bin/make lint` compiles every first-party Python module and the static checker.
- `/usr/bin/make test` runs 29 static contracts and the executable no-network runtime
  tests.
- `/usr/bin/make contract-test` rejects workflow and dependency-lock policy regressions.
- `/usr/bin/make build`, `/usr/bin/make verify`, and `/usr/bin/make check` provide stable repository gates.
- `/usr/bin/make check` removes Python bytecode before and after verification.
- Public Make targets resolve the repository from the loaded Makefile and
  reject unsafe execution modes, caller-controlled roots or shells for the
  sole reviewed Makefile, later single-colon recipe replacement, and Make
  expressions in `PYTHON`. Python verification runs isolated from ambient
  `PYTHONPATH`, user-site packages, and startup hooks.
- Caller-supplied later makefiles, including double-colon public recipes and later override directives, are outside the local Make trust boundary.
- Startup makefiles can run parse-time Make functions before the repository
  Makefile rejects them; run the documented commands without extra `-f` files
  or `MAKEFILES` when collecting local validation evidence.
- GNU Make 4.4 expands Make syntax in a command-line `ROOT` value while
  processing simultaneous command-line overrides, before this Makefile can
  replace `ROOT`. Do not pass Make expressions in `ROOT`; that pre-load
  expression remains caller authority. Environment `ROOT` values are still
  neutralized without expansion.

GitHub Actions installs the exact lock with `--require-hashes` and runs `/usr/bin/make check` on Python 3.10,
3.12, and 3.14 under read-only permissions on Ubuntu 24.04. A separate Python
3.12 job runs the pinned resolved dependency audit. CodeQL analyzes Actions,
Python, and first-party JavaScript; only reviewed vendored Bootstrap is
excluded.

Hosted verification does not contact Meta or MySQL. Live OAuth, Graph friend
access, schema compatibility, and deployed database behavior require an
isolated credentialed smoke test.

The verification authority boundary and adversarial regression matrix are
documented in `docs/plans/2026-06-21-make-authority-isolation.md`.

## Security Contracts

- User, OAuth-state, and OAuth-next cookies are `HttpOnly`, `Secure`, and
  `SameSite=Lax`; OAuth cookies expire after ten minutes and the encrypted user
  session after one day.
- Meta access tokens are encrypted with Fernet before entering signed cookies;
  signing alone is not treated as confidentiality.
- OAuth callbacks validate high-entropy state and redirect only to literal `/`
  or `/events` paths.
- Graph calls use HTTPS bearer headers, finite timeouts, disabled redirects, a
  1 MiB response limit, and generic errors that exclude tokens and response
  bodies.
- Owner/friend checks require an exact matching friend ID.
- Event-scoped attendee, message, vote, suggestion, and availability endpoints
  enforce the same owner-or-friend decision before protected reads or writes.
- Votes require the suggestion to belong to the authorized event before any
  duplicate check, insertion, or deletion.
- Availability replacements validate every submitted time before deleting saved values.
- Availability replacement uses one verified InnoDB transaction so DELETE and
  ordered INSERT statements commit or roll back together.
- PyMySQL operations keep SQL and parameters separate, roll back failed writes,
  and close every connection.
- Tornado XSRF checks protect writes, and state changes remain POST-only.
- Templates use Tornado autoescaping; only generated XSRF form markup is
  rendered explicitly as raw HTML.
- Authenticated profile links derive from the verified Graph user ID and do not
  require an unavailable legacy `link` field in the encrypted session payload.
- Event templates use dictionary access compatible with the configured
  PyMySQL `DictCursor` rows.
- Event templates do not call provider APIs with JSONP or expose provider
  credentials. Existing suggestions remain visible and votable; a future place
  search must be server-mediated with secrets held in deployment configuration.
- Stored suggestion links are revalidated at render time so legacy non-HTTP(S)
  values appear as plain text instead of clickable URLs.
- Cookie, session, Meta, and MySQL secrets must never be committed.

## Maintenance Notes

- See `SECURITY.md` for reporting and safe research guidance.
- See `VISION.md` for product direction and contribution guardrails.
- See `docs/plans/2026-06-12-modern-python-web-runtime.md` for the Python 3,
  Tornado, database, OAuth, encrypted-session, and dependency migration.
- See `docs/plans/2026-06-25-project-status-and-setup.md` for the documented
  maintenance, archive, setup, and hosted-service boundary.
- See `docs/plans/2026-06-12-willbeout-first-party-codeql-remediation.md`
  for the first-party CodeQL alert remediation.
- See `docs/plans/2026-06-13-oauth-error-callbacks.md` for state-bound OAuth
  denial and provider-error handling with query-redacted request logs.
- See `docs/plans/2026-06-13-event-scoped-endpoint-authorization.md` for shared
  authorization across event pages and supporting data endpoints.
- See `docs/plans/2026-06-14-event-vote-user-binding.md` for binding the
  authenticated user to the desktop event page's vote lookup.
- See `docs/plans/2026-06-16-vote-suggestion-event-binding.md` for isolating
  vote mutations to suggestions within the authorized event.
- See `docs/plans/2026-06-25-yelp-jsonp-retirement.md` for retiring the obsolete
  client-side place search while preserving existing suggestion rendering.
- Earlier plans under `docs/plans/` preserve the event access, integer ID,
  XSRF, secure-cookie, HTTPS integration, and CI decisions enforced by
  `make check`.

## Contributing

Keep changes focused, preserve the no-network verification path, update the
relevant plan and contracts with behavior changes, and run `make check` before
handoff. Do not claim live Meta or MySQL behavior without an isolated
credentialed verification record.
