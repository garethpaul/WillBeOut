# WillBeOut First-Party CodeQL Remediation

Status: Completed

## Problem

The current remediation head lacks CodeQL analysis and the default branch has
19 open findings: unsafe auth redirect flows, a polynomial mobile-detection
regular expression, unverified fixed-version mobile CDN resources, and
findings inside a vendored Bootstrap 2.1.0 bundle. The repository also retains
a separate legacy Python 2 dependency backlog that cannot be truthfully fixed
without a broader Tornado/database/runtime migration.

## Plan

1. Replace arbitrary local `next` paths with literal allowlisted return values
   and update login links to request `/events` explicitly.
2. Remove the redundant mobile user-agent detector because both branches
   already redirect to the same destination.
3. Add reviewed SHA-384 integrity hashes and anonymous CORS mode to every
   fixed-version jQuery and jQuery Mobile stylesheet/script.
4. Add immutable-pinned actions, Python, and JavaScript/TypeScript CodeQL
   analysis. Exclude only the used vendored Bootstrap 2.1.0 source, guarded by
   its exact license/version header and SHA-256 digest, while analyzing all
   first-party JavaScript.
5. Extend portable contracts for the redirect allowlist, removed regex,
   reviewed CDN resource inventory, CodeQL config/workflow, and vendored-file
   checksum.
6. Run local/external gates, hostile mutations, live SRI verification, exact
   hosted analysis, and a truthful security-alert audit.

## Verification

- `python3 scripts/check_willbeout_contracts.py` passed all 19 auth, SRI,
  CodeQL-scope, workflow, and repository contracts.
- `python3 scripts/test_workflow_contract.py` passed with all 17 hostile
  workflow mutations rejected.
- `python3 -m py_compile scripts/check_willbeout_contracts.py` passed, and both
  workflow YAML files parsed successfully.
- Live downloads of all four fixed-version CDN assets reproduced the exact
  reviewed SHA-384 values recorded in the templates.
- `make check` passed from the repository root and through an absolute
  Makefile path, including cleanup, compilation, all 19 repository contracts,
  and all 17 workflow mutations; `git diff --check` also passed.
- Seven targeted hostile mutations were rejected: arbitrary redirect
  passthrough, mobile-detector restoration, missing SRI, a broader CodeQL
  exclusion, vendored Bootstrap checksum drift, a mutable action reference,
  and an extra workflow.
- Exact implementation head `0aecde0356502e40d12947fae5d1061d0e69e1ff`
  passed pull-request Check run `27427187249` on Python 3.10, 3.12, and
  3.14, and CodeQL run `27427187289` for actions, Python, and
  JavaScript/TypeScript.
- The implementation-head branch and pull-request refs reported zero open
  CodeQL alerts and zero secret-scanning alerts. The 14 legacy Python 2
  Dependabot alerts remain explicitly deferred to a supported-runtime and
  dependency migration.
- Strict `master` branch protection now requires the three Check and three
  CodeQL contexts; PR #6 was open, clean, and mergeable after the update.
