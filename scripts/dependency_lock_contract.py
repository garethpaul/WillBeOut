import re


EXPECTED_DIRECT = {
    "cryptography": "48.0.1",
    "pymysql": "1.2.0",
    "tornado": "6.5.6",
}
EXPECTED_LOCK = {
    "cffi": ("2.0.0", "platform_python_implementation != 'PyPy'"),
    "cryptography": ("48.0.1", None),
    "pycparser": ("3.0", "implementation_name != 'PyPy' and platform_python_implementation != 'PyPy'"),
    "pymysql": ("1.2.0", None),
    "tornado": ("6.5.6", None),
    "typing-extensions": ("4.15.0", "python_full_version < '3.11'"),
}
EXPECTED_GUIDANCE = {
    "AGENTS.md": (
        "python3 -m pip install --require-hashes -r requirements.lock",
        "uv pip compile requirements.txt --generate-hashes --universal --python-version 3.10 --output-file requirements.lock",
    ),
    "README.md": (
        "python -m pip install --require-hashes -r requirements.lock",
        "uv pip compile requirements.txt --generate-hashes --universal --python-version 3.10 --output-file requirements.lock",
    ),
    "SECURITY.md": ("`--require-hashes`",),
    "VISION.md": ("hash-verified production lock",),
    "CHANGES.md": ("GHSA-537c-gmf6-5ccf",),
    "docs/plans/2026-06-15-hash-verified-production-lock.md": (
        "status: completed",
        "## Work Completed",
        "## Verification Completed",
    ),
}
HASH_PATTERN = re.compile(r"--hash=([^:\s]+):([^\s]+)")
PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s;]+)(?:\s*;\s*(.+))?$")


def normalize_name(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def logical_lines(text):
    current = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        continued = stripped.endswith("\\")
        current.append(stripped[:-1].rstrip() if continued else stripped)
        if not continued:
            yield " ".join(current)
            current = []
    if current:
        yield " ".join(current)


def parse_direct(text, errors):
    packages = {}
    for line in logical_lines(text):
        match = PIN_PATTERN.fullmatch(line)
        if not match or match.group(3):
            errors.append("pin every direct requirement without markers")
            continue
        name = normalize_name(match.group(1))
        if name in packages:
            errors.append("declare each direct requirement once")
        packages[name] = match.group(2)
    return packages


def parse_lock(text, errors):
    packages = {}
    for line in logical_lines(text):
        hashes = HASH_PATTERN.findall(line)
        requirement = HASH_PATTERN.sub("", line).strip()
        match = PIN_PATTERN.fullmatch(requirement)
        if not match:
            errors.append("use only exact pinned requirements and hash options in the lock")
            continue

        name = normalize_name(match.group(1))
        if name in packages:
            errors.append("declare each locked requirement once")
            continue
        if not hashes:
            errors.append("hash every locked requirement")
        for algorithm, digest in hashes:
            if algorithm != "sha256" or not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append("use only complete lowercase SHA-256 hashes")
        packages[name] = (match.group(2), match.group(3), hashes)
    return packages


def validate(direct_text, lock_text):
    errors = []
    direct = parse_direct(direct_text, errors)
    locked = parse_lock(lock_text, errors)

    if direct != EXPECTED_DIRECT:
        errors.append("keep the exact reviewed direct dependency graph")
    if set(locked) != set(EXPECTED_LOCK):
        errors.append("keep the exact reviewed resolved dependency graph")

    for name, (expected_version, expected_marker) in EXPECTED_LOCK.items():
        if name not in locked:
            continue
        version, marker, _hashes = locked[name]
        if version != expected_version:
            errors.append("keep the reviewed {0} version".format(name))
        if marker != expected_marker:
            errors.append("keep the reviewed {0} environment marker".format(name))

    for name, version in direct.items():
        if name in locked and locked[name][0] != version:
            errors.append("keep direct and locked {0} versions aligned".format(name))
    return errors


def validate_guidance(documents):
    errors = []
    for path, snippets in EXPECTED_GUIDANCE.items():
        text = documents.get(path, "")
        for snippet in snippets:
            if text.count(snippet) != 1:
                errors.append("keep exactly one {0} contract in {1}".format(snippet, path))
    return errors
