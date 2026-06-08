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
- Treat Python 2 and old Tornado/Facebook APIs as legacy
- Avoid exposing friend, event, or attendance data

Next priorities:

- Fix syntax and compatibility issues before runtime use
- Add README setup notes and archive status
- Add tests for auth, event access, votes, and availability updates
- Review privacy behavior for friend checks and event visibility

Contribution rules:

- One PR = one focused auth, event, vote, database, template, or documentation change.
- Do not commit credentials or real attendee data.
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
