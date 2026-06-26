## WillBeOut Vision

WillBeOut is a Python 3 Tornado web app for coordinating events, availability,
suggestions, and votes through Facebook authentication and a MySQL database.

The repository is useful as a historical social planning app with Tornado
handlers, Facebook auth, templates, mobile views, voting, availability, and
event pages.

The goal is to preserve the app structure while making credentials, social data,
database safety, and external-service boundaries explicit.

The current focus is:

Priority:

- Preserve event, availability, suggestion, and voting flows
- Keep Facebook and MySQL credentials in deployment configuration
- Keep Tornado cookie signing secrets in deployment configuration
- Keep Facebook access tokens encrypted before secure signed-cookie storage
- Enforce signed-cookie age limits during browser and server verification
- Require POST and Tornado XSRF validation for every authenticated state change
- Keep the Python 3.10+ runtime, hash-verified production lock, and exact
  resolved dependency audit explicit
- Keep OAuth state bound to secure cookies and callback URLs configured as HTTPS
- Keep Meta Graph calls bounded, redacted, and exact-ID authorization based
- Keep PyMySQL operations parameterized with deterministic cleanup
- Enforce owner/friend access before rendering event details
- Enforce owner/friend access before rendering mobile event details
- Enforce the same owner/friend access before every event-scoped supporting API
  read or write
- Return missing desktop events before reading owner fields
- Validate event ids before querying event detail data
- Validate vote ids before writing or deleting vote data
- Bind vote suggestions to the authorized event before storage
- Validate attendee event ids before reading or writing attendance data
- Validate availability event ids before reading or writing availability data
- Validate complete availability payloads before replacing saved values
- Replace availability atomically on a verified transactional table
- Validate message event and delete ids before reading or writing message data
- Render decoded message content through DOM text APIs instead of HTML parsing
- Keep generated desktop metadata out of source control
- Keep active template-side external integrations on HTTPS
- Keep the dependency-free `make check` baseline running in GitHub Actions
- Keep hosted verification read-only, credential-free, pinned, and protected
  against structural workflow regressions
- Avoid exposing friend, event, or attendance data

Next priorities:

- Exercise the modern Meta and MySQL integrations in an isolated credentialed environment
- Add README setup notes and archive status
- Add tests for auth, event access, votes, and availability updates
- Keep `make check` covering auth and secret-configuration contracts
- Add runtime tests for missing-event and denied-access paths

Contribution rules:

- One PR = one focused auth, event, vote, database, template, or documentation change.
- Do not commit credentials or real attendee data.
- Do not commit generated desktop metadata or local environment files.
- Keep SQL parameterized and access checks visible.
- Keep framework and dependency changes backed by executable no-network tests.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

The app handles social identities, event attendance, availability, and places.
It should keep data access scoped, credentials secret, and privacy expectations
clear before any deployment.

## What We Will Not Merge (For Now)

- Plaintext credentials
- Real attendee or friend datasets
- Public deployment without access/privacy review
- Framework rewrites that hide authorization behavior

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
