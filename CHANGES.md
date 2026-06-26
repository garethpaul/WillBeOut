# Changes

## 2026-06-26 13:39 PDT - P2 - Harden calendar JSON responses

### Summary
The authenticated calendar read endpoint now serves private availability rows
with an explicit JSON media type and `nosniff` while preserving its array shape.

### Work completed
- Added the same response-header boundary already used by the message API.
- Added a real authenticated Tornado request covering headers, decoded payload,
  and exact user/week query parameters.
- Added a 33rd static contract, synchronized security and runtime guidance, and
  durable design and implementation plans.

### Threads
- Started: calendar JSON response boundary — completed directly.
- Continued: no-network runtime coverage and historical-app privacy hardening.
- Stopped: none.

### Files changed
- `cal.py` and `test_modern_runtime.py` — response fix and regression test.
- `scripts/check_willbeout_contracts.py` — static and plan contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, and `docs/plans/` — maintained guidance.

### Validation
- RED: focused runtime test received `text/html; charset=UTF-8` before the fix.
- GREEN: focused runtime test passed after the two response headers were added.
- The first full baseline attempt used system Python without locked dependencies
  and failed importing `cryptography`; the reviewed `.venv` interpreter passed
  the complete baseline.
- The first green test fixture bypassed query-call recording; the test-only
  fixture was corrected before final validation without changing production code.
- The first static-contract run rejected the plan because it did not contain
  the canonical `make check` evidence phrase; the plan wording was corrected.
- Root and external-directory `make check` passed 33 static contracts, 41
  no-network runtime tests, 31 workflow mutations, 23 dependency-lock
  mutations, lint, build, and Make authority checks.
- The default isolated `pip-audit` run failed creating its temporary pip
  environment; the exact fully pinned lock then passed with no known
  vulnerabilities under `--no-deps --disable-pip`.
- `git diff --check` and current-tree/added-line secret scans passed. History
  scanning surfaced two pre-existing generic-key findings in old commits;
  neither is in the current tree and GitHub secret scanning has no open alert.

### Bugs / findings
- P2 privacy: direct calendar API navigation used an ambiguous HTML media type
  for authenticated user availability data.

### Blockers
- Live Meta and MySQL integration remains a credentialed environment boundary.

### Next action
- Run full lock, audit, review, hosted CI, and exact-head merge gates.

## 2026-06-26T04:59:28-0700 — P3 documentation — cycle: runtime test roadmap

- Cycle: refreshed the newly merged default branch and compared its 40-test
  no-network runtime suite with the remaining roadmap.
- Finding: `VISION.md` still asked for auth, event-access, vote, and availability
  tests even though all four areas now have executable coverage.
- Work: replaced the stale future item with a maintained coverage invariant and
  documented OAuth/cookie, protected-event, vote-binding, and atomic
  availability coverage in `README.md`.
- Contracts: added a 32nd static contract tied to representative runtime test
  names, the README inventory, vision invariant, retired priority, and completed
  plan evidence.
- Validation: the contract failed first on the missing README inventory. Full
  repository, external Make, hostile mutation, dependency health/audit,
  compilation, bytecode cleanup, and diff evidence is recorded in the plan.

## 2026-06-26T03:10:58-0700 — P1 tests — cycle: event authorization edge matrix

- Cycle: selected the remaining portable authorization-test roadmap gap after
  provider and credentialed integration work remained blocked.
- Finding: denied-access tests covered all protected event routes but omitted
  transactional writes, while missing-event 404 behavior executed only the
  message read path.
- Work: centralized five protected reads and eight protected writes, exercised
  both 403 and 404 boundaries across the full matrix, and asserted no Facebook
  lookup, query, execute, rowcount, or transaction follows a missing event.
- Files: expanded `test_modern_runtime.py`, strengthened the static contract,
  reconciled README/VISION, and added the completed test plan.
- Validation: the focused 18-test authorization class passed; a temporary
  mutation removing the message access check failed with `404 != 200` on the
  new missing-event matrix. Checkout and external-root `make check` passed 31
  static contracts, 40 no-network runtime tests, 31 workflow mutations, 23 lock
  mutations, and 40 Make authority cases. Dependency health, audit, compilation,
  and diff checks passed with no known vulnerabilities.
- Blockers: none for no-network verification; hosted Python and CodeQL remain
  exact-head authority.
- Next: run exact-head review, hosted CI, and merge.

## 2026-06-25T21:13:30-0700 — P3 documentation — cycle: project status and setup

- Cycle: selected the highest actionable WillBeOut roadmap item after the
  provider and live-integration priorities remained credential-dependent.
- Finding: the README already documented environment creation, hash-verified
  installation, required secrets, Meta/MySQL configuration, and the local entry
  point, but it did not distinguish repository maintenance from hosted-service
  operation or state the current GitHub archive status.
- Work: added an explicit maintained-historical-project status, recorded that
  the repository was not archived on GitHub when verified on June 25, 2026,
  preserved the credentialed setup boundary, linked a completed plan, and
  removed the stale combined roadmap item.
- Files: updated README, VISION, AGENTS, the static contract, this log, and
  `docs/plans/2026-06-25-project-status-and-setup.md`.
- Validation: the new contract failed on the missing status section before the
  documentation was added. An isolated hash-verified environment then passed
  `make check` with 31 static contracts, 39 no-network runtime tests, 31 workflow
  mutations, 23 lock mutations, and 40 Make authority cases; `pip check`, Python
  compilation, dependency audit, and diff checks passed with no known
  vulnerabilities. Three hostile documentation mutations were rejected.
- Blockers: no documentation blocker remains; live Meta/MySQL verification and
  any replacement place provider still require isolated credentials.
- Next: complete exact-head review, hosted CI, and merge.

## 2026-06-25T18:33:31-0700 — P1 security — cycle: retired Yelp JSONP integration

- Cycle: inspected public open work, green default branches, persisted plans,
  event templates, suggestion storage, tests, and provider documentation.
- Threads: four investigators reviewed the executable provider boundary, user
  experience, dependency-free contracts, and repository history.
- Bug: desktop and mobile event pages exposed Yelp's retired v1 search through
  JSONP, embedded a legacy provider credential, executed remote responses as
  JavaScript, and assembled provider-controlled fields into HTML strings.
- Work: removed the dead search controls and scripts from both templates while
  preserving stored suggestion rendering, desktop voting, mobile places, and
  mobile messaging. Added a dedicated regression contract and documented that
  future provider search must be server-mediated with private credentials.
  Revalidated legacy stored URLs at render time so unsafe schemes appear as
  plain suggestion names rather than links.
- Validation: RED failed on the live Yelp endpoint. Full `make check` passes with
  30 static contracts, 39 runtime tests, 54 workflow/lock mutations, lint, and
  Make authority; dependency health and `git diff --check` pass. Eleven hostile
  mutations restoring provider execution/UI or removing preserved suggestion,
  voting, messaging, and stored-link protections are rejected; harmless
  non-API Yelp attribution remains allowed.
- Blockers: live provider replacement is intentionally out of scope because it
  requires a private API key, server request handling, response validation, and
  product/privacy decisions.
- Next: complete independent re-review, exact-head Codex review, hosted CI, and
  merge.

## 2026-06-25T18:15:09-0700 — P0 security — cycle: stored message rendering XSS

- Cycle: inspected public open work, green main-branch workflows, persisted risks,
  WillBeOut message creation, storage, API decoding, templates, tests, and plans.
- Threads: four investigators reviewed handler ordering, history, contracts, and
  adversarial input semantics; their review exposed a higher-priority rendering sink.
- Bug: both desktop and mobile event views concatenated decoded `val.msg` content
  into HTML strings before DOM insertion, allowing stored messages to create
  executable markup for authorized event viewers.
- Work: replaced string-built message rows with DOM construction, assigned message
  and date values through `.text()`, encoded profile path components, and added a
  mutation-sensitive static security contract plus policy documentation. The
  message API now returns non-sniffable JSON for direct navigation.
- Files: changed both event templates, the static checker, README, SECURITY,
  VISION, this log, and the message-rendering implementation plan.
- Validation: RED failed on the desktop HTML sink and inspection confirmed the
  same mobile pattern. Full `make check` passes with 29 static contracts, 38
  runtime tests, 54 workflow/lock mutations, lint, and Make authority; both
  renderer mutations are rejected and hostile direct JSON content stays data.
- Findings: blank/length validation remains desirable, but no live schema limit is
  documented and desktop/mobile length semantics differ; that policy is deferred.
- Blockers: none for the XSS fix; live Meta/MySQL integration remains out of scope.
- Next: complete re-review, exact-head Codex review, hosted CI, and merge.

## 2026-06-25

- Restored authorized mobile event rendering with dictionary access compatible
  with PyMySQL `DictCursor` rows.
- Bound mobile suggestion vote counts to the requested event, matching the
  desktop event query and preventing cross-event vote rows from being counted.

## 2026-06-21

- Documented and reproduced GNU Make 4.4's command-line `ROOT` pre-load
  expression boundary without weakening environment-root neutralization.
- Isolated repository verification from caller-controlled shell state,
  execution modes, root overrides, Python expressions, and later single-colon
  public recipe replacement for the sole reviewed Makefile path.
- Documented caller-supplied later makefiles, later override directives, and startup parse-time Make code as outside the local Make trust boundary.
- Added adversarial Make authority coverage and bound hosted verification to
  `/usr/bin/make` without changing service behavior or dependencies.

## 2026-06-19

- Rejected non-ASCII OAuth callback state without raising an internal error.
- Preserved raw suggestion text for single-pass template autoescaping and
  rejected non-HTTP(S) suggestion links before storage.
- Removed inline event-name JavaScript from share links and isolated external
  suggestion links from their opener without double-loading the share handler.
- Restricted availability to unique rendered hours, allowed atomic clearing, and
  kept the submitted payload synchronized after client-side deselection.

## 2026-06-16

- Validated complete availability payloads before deleting or inserting saved times.
- Made availability replacement atomic on verified InnoDB storage.
- Updated the hash-locked Tornado runtime from 6.5.6 to 6.5.7 to remediate
  GHSA-pw6j-qg29-8w7f while preserving the reviewed resolved graph.
- Blocked cross-event vote creation and deletion by requiring each suggestion
  ID to belong to the already authorized event before vote storage is touched.

## 2026-06-15

- Added SHA-256 artifact hashes to the resolved production lock and made
  canonical pip installs fail closed with `--require-hashes`.
- Updated cryptography from 48.0.0 to 48.0.1 after the pinned audit identified
  GHSA-537c-gmf6-5ccf in the original exact pin.
- Added semantic lock contracts and hostile mutations for missing hashes,
  weak algorithms, dependency drift, marker loss, and unhashed workflow paths.

## 2026-06-14

- Fixed authorized desktop event pages to bind the authenticated user ID before
  loading that user's votes.
- Derived authenticated Facebook profile links from the verified user ID
  instead of requiring the unavailable legacy Graph `link` field.
- Made the event share action use dictionary access compatible with PyMySQL
  `DictCursor` rows.
- Added a no-network owner-page regression and mutation-sensitive static
  coverage for the parameterized vote lookup.

## 2026-06-13

- Enforced the documented one-day user session and ten-minute OAuth cookie
  lifetimes during server-side signed-cookie verification.
- Centralized owner-or-Facebook-friend authorization and applied it before all
  event-scoped attendee, message, vote, suggestion, and availability access.

## 2026-06-12

- Migrated first-party modules from Python 2 syntax and removed Tornado APIs
  deleted before Tornado 6.
- Replaced the vulnerable legacy requirement set with exact Tornado 6.5.6,
  PyMySQL 1.2.0, and cryptography 48.0.0 pins plus a five-package lock.
- Replaced `tornado.database` with a parameterized PyMySQL adapter that rolls
  back failed writes and closes every connection.
- Replaced the removed Facebook mixin with an explicit Graph API v24.0 client,
  configured HTTPS callback, OAuth state binding, bounded responses, and
  redacted errors.
- Encrypted Facebook access tokens before signed-cookie storage and enabled
  template autoescaping with explicit raw XSRF form markup.
- Added executable no-network runtime tests and a resolved dependency-audit
  job while preserving the existing first-party security contracts.

- Restricted authentication return paths to literal `/` and `/events`
  destinations and removed the redundant high-cost mobile user-agent regex.
- Added reviewed SRI and anonymous CORS attributes to fixed-version jQuery and
  jQuery Mobile resources.
- Added immutable-pinned CodeQL analysis for actions, Python, and first-party
  JavaScript, with an exact checksum guard around the sole vendored Bootstrap
  exclusion.
- Removed the unused duplicate minified Bootstrap bundle and expanded
  `make check` contracts for the security and analysis scope.

## 2026-06-10

- Enabled Tornado XSRF enforcement, converted attendance, voting, message
  deletion, and logout mutations from GET to POST, and added tokens to native
  forms and all same-origin AJAX writes.
- Added a pinned, read-only GitHub Actions workflow that runs `make check` on
  Python 3.10, 3.12, and 3.14 for the dependency-free Tornado handler contract
  baseline with credential-free checkout.
- Added dependency-free workflow tests that reject contradictory credentials,
  write permissions, unreviewed actions, and weakened CI commands.
- Guarded the legacy Python 2 syntax step so hosted CI can run the baseline
  when Python 2 is unavailable.
- Replaced active template-side jQuery, Facebook, Yelp, and share/profile HTTP
  integrations with HTTPS and added static coverage.
- Marked the signed Facebook user cookie `HttpOnly` and `Secure` so the browser
  does not expose it to JavaScript or send it over plain HTTP.
- Pinned hosted verification to Ubuntu 24.04 with superseded-run cancellation
  and made Make targets independent of the caller's working directory.

## 2026-06-09

- Removed tracked macOS metadata and added static checker coverage to keep it
  out of source control.
- Added shared integer request validation for message event ids and
  delete-message ids.
- Added static checker coverage for malformed message id handling.
- Added shared integer request validation for attendance event ids.
- Added static checker coverage for malformed attendance event id handling.
- Added shared integer request validation for availability event ids.
- Added static checker coverage for malformed availability event id handling.
- Added shared integer request validation for desktop and mobile event ids.
- Added static checker coverage for malformed event id handling.
- Added shared integer request validation for vote and change-vote ids.
- Added static checker coverage for malformed vote id handling.
- Returned 404 for missing desktop events before reading owner fields or
  querying related suggestions.
- Added static checker coverage for the desktop missing-event guard.
- Enforced owner/friend access before rendering mobile event details and
  returned 404 for missing mobile events.
- Added static checker coverage for the mobile event access contract.

## 2026-06-08

- Enforced event owner/friend access before rendering event details.
- Restricted Facebook login `next` redirects to local absolute paths.
- Standardized docs-plan completion status while preserving `make check`
  evidence enforcement.
- Removed a stray non-code suffix from the Facebook auth redirect path.
- Added static contracts for the configured Tornado cookie secret.
- Added `make verify`/`make check` verification and Python 2 syntax checks.
