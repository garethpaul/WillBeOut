# Calendar JSON Response Headers Implementation Plan

Status: Completed

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Return authenticated calendar data with an explicit non-sniffable JSON response while preserving the existing payload contract.

**Architecture:** Keep `CalHandler.get` as the owner of calendar serialization and set response metadata before any database access. Reuse the established message API header contract and verify it through both a real Tornado request and static source checks.

**Tech Stack:** Python 3.10+, Tornado 6.5.7, `unittest`, repository contract checker, GNU Make.

---

### Task 1: Prove the missing response boundary

**Files:**
- Modify: `test_modern_runtime.py`

**Step 1: Write the failing test**

Add an authenticated `/calendar/get?wk=26` request whose fake database returns
one calendar row. Assert status 200, exact JSON and `nosniff` headers, decoded
array contents, and the user/week query parameters.

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -B -m unittest test_modern_runtime.EventEndpointAuthorizationTest.test_calendar_api_uses_non_sniffable_json`

Expected: FAIL because `Content-Type` is still Tornado's HTML default.

### Task 2: Add the minimal handler fix

**Files:**
- Modify: `cal.py`

**Step 1: Write minimal implementation**

Set `Content-Type` to `application/json; charset=UTF-8` and
`X-Content-Type-Options` to `nosniff` before the existing query and write.

**Step 2: Run test to verify it passes**

Run: `.venv/bin/python -B -m unittest test_modern_runtime.EventEndpointAuthorizationTest.test_calendar_api_uses_non_sniffable_json`

Expected: PASS with the unchanged array payload.

### Task 3: Preserve the contract and maintenance record

**Files:**
- Modify: `scripts/check_willbeout_contracts.py`
- Modify: `README.md`
- Modify: `SECURITY.md`
- Modify: `VISION.md`
- Modify: `CHANGES.md`
- Modify: `docs/plans/2026-06-26-calendar-json-response.md`

**Step 1: Add static and documentation contracts**

Require both headers in `CalHandler.get`, document the direct-navigation
privacy boundary, mark this plan completed, and add the cycle record.

**Step 2: Run full validation**

Run: `/usr/bin/make PYTHON="$PWD/.venv/bin/python" check`

Expected: 41 runtime tests plus all static, workflow, dependency-lock, lint,
and Make authority checks pass.

Run: `uvx --from pip-audit==2.10.0 pip-audit -r requirements.lock`

Expected: no known vulnerabilities.

Run: `git diff --check && gitleaks dir . --no-banner && gitleaks git . --no-banner`

Expected: clean diff and no leaks.

## Verification Results

- RED: the authenticated runtime test received `text/html; charset=UTF-8` from
  `/calendar/get` before the handler fix.
- GREEN: the focused test passes with the exact JSON and `nosniff` headers, the
  unchanged decoded array, and the authenticated user/week query parameters.
- Root and external-directory `make check` pass 33 static contracts, 41
  executable runtime tests, 31 workflow mutations, 23 dependency-lock
  mutations, lint, build, and Make authority checks.
- `pip-audit` found no known vulnerabilities in the fully pinned lock using
  `--no-deps --disable-pip` after its default temporary-venv bootstrap failed.
- Current-tree and added-line secret scans are clean. The history scan reports
  two pre-existing generic-key findings from old commits, neither present in
  the current tree; GitHub secret scanning has no open alert.
- Hosted checks remain exact-head merge gates.

### Task 4: Ship the exact reviewed head

**Files:**
- No additional source files.

**Step 1: Commit and push**

Commit the focused change and open a PR against `master`.

**Step 2: Review and merge**

Run the Codex branch review, wait for all hosted Python, dependency-audit, and
CodeQL checks, verify local/remote/PR head equality, and merge only that SHA.
