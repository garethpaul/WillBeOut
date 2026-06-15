# Security Policy

## Supported Versions

The supported security scope for `WillBeOut` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: This is the repo for willbeout.com

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/WillBeOut` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a Python web API or service project. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- Dependency manifests detected: requirements.txt. Dependency updates should preserve lockfiles when present and avoid introducing packages without a clear maintenance reason.
- Tornado secure-cookie signing should use `COOKIE_SECRET` from deployment
  configuration. Do not replace it with a checked-in literal secret.
- The signed Facebook user cookie contains Fernet-encrypted authentication data
  and must remain `HttpOnly`, `Secure`, and `SameSite=Lax`. Signing alone is not
  confidentiality. Server-side verification must enforce the same one-day user
  and ten-minute OAuth lifetimes used for browser expiry;
  `SESSION_ENCRYPTION_KEY` must remain separate from
  `COOKIE_SECRET` and out of source control.
- OAuth callbacks must use the configured HTTPS `FACEBOOK_REDIRECT_URI`, bind a
  high-entropy state value to a secure cookie, and retain the local-only next
  redirect allowlist.
- Meta Graph requests must use HTTPS bearer headers, bounded timeouts and
  response sizes, and generic errors that exclude tokens and response bodies.
- PyMySQL queries must keep SQL and parameters separate, roll back failed
  writes, and close connections on all paths.
- Tornado template autoescaping must remain enabled; only generated XSRF form
  markup may use explicit raw rendering.
- Request IDs for event, vote, attendee, availability, and message handlers
  should be validated before database access or redirects.
- Active template-side external integrations should use HTTPS to avoid mixed
  content and request tampering.
- Post-login redirects are restricted to the literal `/` and `/events`
  destinations; do not restore arbitrary `next` values or user-agent regex
  routing in the authentication flow.
- Fixed-version jQuery and jQuery Mobile resources use reviewed SHA-384 SRI
  hashes with anonymous CORS. Treat URL, version, hash, and tag-count changes
  as supply-chain changes requiring review.
- GitHub Actions installs the exact production lock with pip hash verification
  and runs `make check` with
  immutable actions, fixed Ubuntu runners, read-only permissions,
  credential-free checkout, superseded-run cancellation, and structural policy mutations;
  review workflow, checker, and template integration changes as part of the
  supply-chain surface.
- CodeQL analyzes actions, Python, and first-party JavaScript. Only the used
  vendored Bootstrap 2.1.0 source is excluded, and its exact header and digest
  are contract-checked. A separate pinned job audits the resolved production
  graph. Live Meta and MySQL behavior remains a credentialed test boundary.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

Event pages and their attendee, message, vote, suggestion, and availability
endpoints require the current user to own the event or exactly match the
owner's Facebook friend ID before event-scoped data is read or changed. Missing
events return 404, while existing unauthorized events return 403 without
performing protected data queries or mutations.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Production lock entries must remain exactly pinned with reviewed SHA-256 hashes, and canonical installs must use pip's `--require-hashes` mode. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
