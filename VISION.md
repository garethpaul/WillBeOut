## WillBeOut Vision

WillBeOut is a legacy Tornado web app for coordinating events, availability,
suggestions, and votes through Facebook authentication and a MySQL database.

The repository is useful as a historical social planning app with Tornado
handlers, Facebook auth, templates, mobile views, voting, availability, and
event pages.

The goal is to preserve the app structure while making credentials, social data,
database safety, and framework age explicit.

The current focus is:

Priority:

- Preserve event, availability, suggestion, and voting flows
- Keep Facebook and MySQL credentials in deployment configuration
- Keep Tornado cookie signing secrets in deployment configuration
- Keep the signed Facebook user cookie restricted to HTTPS and inaccessible to
  browser JavaScript
- Require POST and Tornado XSRF validation for every authenticated state change
- Treat Python 2 and old Tornado/Facebook APIs as legacy
- Enforce owner/friend access before rendering event details
- Enforce owner/friend access before rendering mobile event details
- Return missing desktop events before reading owner fields
- Validate event ids before querying event detail data
- Validate vote ids before writing or deleting vote data
- Validate attendee event ids before reading or writing attendance data
- Validate availability event ids before reading or writing availability data
- Validate message event and delete ids before reading or writing message data
- Keep generated desktop metadata out of source control
- Keep active template-side external integrations on HTTPS
- Keep the dependency-free `make check` baseline running in GitHub Actions
- Avoid exposing friend, event, or attendance data

Next priorities:

- Fix syntax and compatibility issues before runtime use
- Add README setup notes and archive status
- Add tests for auth, event access, votes, and availability updates
- Keep `make check` covering auth and secret-configuration contracts
- Add runtime tests for missing-event and denied-access paths

Contribution rules:

- One PR = one focused auth, event, vote, database, template, or documentation change.
- Do not commit credentials or real attendee data.
- Do not commit generated desktop metadata or local environment files.
- Keep SQL parameterized and access checks visible.
- Separate framework modernization from product behavior changes.

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
