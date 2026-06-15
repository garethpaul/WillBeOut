# AGENTS.md

## Repository purpose

`garethpaul/WillBeOut` is a Python web API or service project. This is the repo for willbeout.com

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `templates` - server-rendered templates
- `requirements.txt` - Python runtime dependencies
- `requirements.lock` - exact resolved production dependency graph
- `test_modern_runtime.py` - executable fake-client runtime tests

## Development commands

- Install dependencies: `python3 -m pip install --require-hashes -r requirements.lock`
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Workflow contract mutations: `make contract-test`
- Tests: `make test`
- Build: `make build`
- Dependency audit: `pip-audit -r requirements.lock`
- Regenerate the lock after reviewed manifest changes: `uv pip compile requirements.txt --generate-hashes --universal --python-version 3.10 --output-file requirements.lock`

## Coding conventions

- Language mix noted in the README: Python (24), JavaScript (12), shell (1).
- Keep runtime tests dependency-injected and no-network.
- Keep Tornado 6.5.6, PyMySQL 1.2.0, cryptography 48.0.1, and the hash-verified resolved lock exact.

## Testing guidance

- `test_modern_runtime.py` covers the executable modern boundary; treat
  `make check` as the minimum baseline.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.
- Keep hosted verification read-only and credential-free with immutable action
  pins; update structural workflow mutations with intentional policy changes.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- `COOKIE_SECRET` configures Tornado secure-cookie signing and must not be committed.
- `SESSION_ENCRYPTION_KEY` encrypts access tokens before signed-cookie storage.
- `FACEBOOK_REDIRECT_URI` must be an exact registered HTTPS callback.
- Keep Meta and MySQL configuration out of git and tests no-network.
- Do not disable template autoescaping or render untrusted values with `raw`.
- Do not commit generated Python bytecode, local virtual environments, or `.env` files.
- Do not commit generated desktop metadata such as `.DS_Store`.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
