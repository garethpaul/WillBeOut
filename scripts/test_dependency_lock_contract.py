#!/usr/bin/env python3
import re
from pathlib import Path

from dependency_lock_contract import EXPECTED_GUIDANCE, validate, validate_guidance


ROOT = Path(__file__).resolve().parents[1]
DIRECT = (ROOT / "requirements.txt").read_text(encoding="utf-8")
LOCK = (ROOT / "requirements.lock").read_text(encoding="utf-8")
GUIDANCE = {path: (ROOT / path).read_text(encoding="utf-8") for path in EXPECTED_GUIDANCE}


def reject(description, direct_text=DIRECT, lock_text=LOCK):
    if not validate(direct_text, lock_text):
        raise AssertionError("{0} mutation was accepted".format(description))


errors = validate(DIRECT, LOCK)
if errors:
    raise AssertionError("baseline dependency lock invalid: {0}".format(errors))
guidance_errors = validate_guidance(GUIDANCE)
if guidance_errors:
    raise AssertionError("baseline dependency guidance invalid: {0}".format(guidance_errors))

unhashed_tornado = re.sub(
    r"(?ms)^(tornado==.*?)(?=^[A-Za-z0-9_.-]+==|\Z)",
    "tornado==6.5.6\n",
    LOCK,
    count=1,
)
mutations = {
    "missing hashes": (DIRECT, unhashed_tornado),
    "wrong hash algorithm": (DIRECT, LOCK.replace("--hash=sha256:", "--hash=sha512:", 1)),
    "short hash": (DIRECT, re.sub(r"sha256:[0-9a-f]{64}", "sha256:abcd", LOCK, count=1)),
    "unpinned requirement": (DIRECT, LOCK.replace("pymysql==1.2.0", "pymysql>=1.2.0", 1)),
    "version drift": (DIRECT, LOCK.replace("tornado==6.5.6", "tornado==6.5.5", 1)),
    "unexpected package": (DIRECT, LOCK + "example==1.0 --hash=sha256:" + "0" * 64 + "\n"),
    "missing Python 3.10 marker": (DIRECT, LOCK.replace(" ; python_full_version < '3.11'", "", 1)),
    "direct and lock drift": (DIRECT.replace("PyMySQL==1.2.0", "PyMySQL==1.1.2"), LOCK),
}
for description, texts in mutations.items():
    reject(description, *texts)

guidance_mutations = 0
for path, snippets in EXPECTED_GUIDANCE.items():
    for snippet in snippets:
        changed = dict(GUIDANCE)
        changed[path] = changed[path].replace(snippet, "", 1)
        if not validate_guidance(changed):
            raise AssertionError("missing {0} guidance mutation was accepted".format(path))
        guidance_mutations += 1

print(
    "dependency lock contract tests passed ({0} mutations rejected).".format(
        len(mutations) + guidance_mutations
    )
)
