# Hash-Verified Production Lock

status: completed

## Context

WillBeOut's maintained Python runtime already uses exact direct pins in
`requirements.txt` and an exact resolved graph in `requirements.lock`.
Canonical CI installs that graph with ordinary `pip install -r`, however, so
the selected versions are fixed while the downloaded distribution artifacts
are not locally authenticated.

Pip's secure-install guidance treats hash checking as an all-or-nothing mode:
every requirement must be pinned and carry one or more locally recorded
hashes. Pip also supports `--require-hashes` as an explicit fail-closed install
contract. The current dependency graph is already exact, making artifact hash
verification a narrow supply-chain hardening step. During implementation, the
pinned audit identified GHSA-537c-gmf6-5ccf in cryptography 48.0.0; the fix
therefore includes the minimum cryptography 48.0.1 patch update.

Primary references:

- <https://pip.pypa.io/en/stable/topics/secure-installs/>
- <https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-require-hashes>
- <https://docs.astral.sh/uv/pip/compile/>

## Priority

Require every canonical production dependency install to authenticate the
resolved artifacts before arbitrary package code can execute. Preserve the
existing Tornado, PyMySQL, cffi, and pycparser versions, with only the audited
cryptography 48.0.1 patch update, and the supported Python 3.10, 3.12, and
3.14 matrix. Resolution also retains
`typing-extensions` only for Python below 3.11, where cryptography requires it.

## Requirements

- Keep the three direct dependencies exactly pinned and update only
  cryptography from 48.0.0 to the audited 48.0.1 fix.
- Regenerate `requirements.lock` as the same exact version graph plus the
  Python 3.10-only `typing-extensions` transitive requirement, with
  SHA-256 hashes for all compatible published artifacts needed by the
  supported runtime matrix.
- Require hash checking explicitly in the canonical CI installation command.
- Keep dependency auditing pinned and pointed at the resolved production lock.
- Add parser-based static contracts that reject missing hashes, unpinned
  entries, unexpected packages, non-SHA-256 hashes, and direct/lock version
  drift without coupling tests to generated formatting.
- Extend workflow mutations to reject removal of hash enforcement or fallback
  to unhashed direct-manifest installation.
- Update README, security, vision, changes, and contributor guidance so local
  installation and maintenance commands match the enforced workflow.
- Preserve no-network runtime tests, workflow permissions, immutable actions,
  application behavior, and the existing stacked pull-request order.

## Implementation Units

### 1. Generate The Hash-Verified Lock

Use the existing exact direct manifest as the source and generate a universal
requirements-format lock with SHA-256 hashes. Confirm the package names and
versions remain exactly cffi 2.0.0, cryptography 48.0.1, pycparser 3.0,
PyMySQL 1.2.0, and Tornado 6.5.6, with typing-extensions 4.15.0 selected only
for Python below 3.11. Do not upgrade direct dependencies or change the
installed graph for any supported runtime in this change.

Files:

- `requirements.lock`

### 2. Enforce And Test Hash Checking

Change the canonical workflow install to use `--require-hashes`. Replace the
current exact-text lock assertion with a small structured requirements parser
that verifies the allowed graph, exact versions, and per-entry SHA-256 hashes.
Extend workflow contracts and mutation tests so an unhashed install, missing
flag, direct-manifest install, or weakened dependency audit fails closed.

Files:

- `.github/workflows/check.yml`
- `scripts/check_willbeout_contracts.py`
- `scripts/workflow_contract.py`
- `scripts/test_workflow_contract.py`

### 3. Synchronize Maintainer Guidance And Evidence

Document hash-verified installation and lock regeneration without presenting
the generated lock as hand-maintained source. Record the unchanged dependency
versions, completed local verification, hostile mutation results, and exact
hosted evidence after implementation.

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `AGENTS.md`
- `docs/plans/2026-06-15-hash-verified-production-lock.md`

## Verification

- Parse the generated lock and prove the exact conditional six-entry graph, exact
  versions, at least one SHA-256 hash per entry, and no unhashed requirement.
- Install the lock in disposable Python 3.10, 3.12, and 3.14 environments with
  `python -m pip install --require-hashes -r requirements.lock`.
- Run `python -m pip check` and `pip-audit -r requirements.lock` in the clean
  Python 3.12 environment.
- Run focused static and workflow mutation tests.
- Run repository-root and external-directory `make check`.
- Reject isolated mutations for missing hashes, wrong algorithms, version
  drift, unexpected packages, removed `--require-hashes`, direct-manifest
  installation, missing guidance, and incomplete plan status.
- Audit the exact diff, generated artifacts, whitespace, conflict markers,
  executable modes, and added credential-like values.
- Require the stacked pull request's exact-head canonical checks and code
  scanning to complete without failure before recording terminal evidence.

## Scope Boundaries

- Do not change application code, dependency versions beyond the minimum
  cryptography 48.0.1 security fix, or public behavior.
- Do not add a new runtime package manager to production or CI; lock generation
  may use a disposable local tool, while installation remains standard pip.
- Do not require source-only distributions; hashes must preserve compatible
  wheels across the supported Python and Linux matrix.
- Do not merge or close the existing pull-request stack without explicit owner
  authorization.

## Risks

- Omitting hashes for a compatible wheel can make one supported Python version
  fail while another succeeds; the full matrix must perform real clean
  installs.
- Generated requirements formatting can change between tooling versions;
  contracts must parse semantics rather than assert the entire file verbatim.
- Hash verification authenticates selected artifacts but does not make a
  vulnerable dependency safe; the existing pinned dependency audit remains
  required.

## Work Completed

- Regenerated the universal production lock with SHA-256 hashes for every
  compatible artifact and retained the Python 3.10-only typing-extensions
  marker required by cryptography.
- Updated cryptography from 48.0.0 to 48.0.1 after the pinned audit identified
  GHSA-537c-gmf6-5ccf, then regenerated and revalidated the exact lock.
- Made the canonical workflow install use pip's explicit `--require-hashes`
  mode while preserving the pinned dependency audit and supported matrix.
- Added semantic direct/lock validation plus dependency and workflow mutation
  suites that reject graph, marker, hash, and install-policy regressions.
- Synchronized contributor, setup, security, vision, and change guidance with
  the enforced hash-verified installation contract.

## Verification Completed

- Installed the exact tracked lock with standard pip and `--require-hashes`
  in clean Python 3.10, 3.12, and 3.14 environments; all three `pip check`
  runs reported no broken requirements.
- Ran `pip-audit==2.10.0 -r requirements.lock` after the cryptography update;
  it reported no known vulnerabilities.
- Rejected all 18 dependency-lock and guidance mutations and all 21 workflow
  mutations.
- Ran all 22 executable no-network runtime tests successfully on the exact
  Python 3.12 dependency graph.
- Ran the full `make check` gate successfully from both the repository root
  and an external `/tmp` working directory; each run passed 23 static
  contracts, 22 runtime tests, and the then-current 28 mutations. After review
  expanded guidance and extra-install coverage, the focused suites rejected
  all 39 mutations.
