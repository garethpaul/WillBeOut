#!/usr/bin/env python3
"""Static safety contracts for the legacy WillBeOut Tornado app."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "auth.py"
FACEBOOK = ROOT / "facebook.py"
PLAN = ROOT / "docs" / "plans" / "2026-06-08-cookie-secret-contract.md"
GITIGNORE = ROOT / ".gitignore"


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def test_auth_handler_has_no_stray_non_code_suffix():
    source = AUTH.read_text()
    assert_true("åå" not in source, "auth.py must not contain stray non-code suffixes")


def test_cookie_secret_comes_from_configuration():
    source = FACEBOOK.read_text()
    assert_true("COOKIE_SECRET" in source, "facebook.py must read COOKIE_SECRET from configuration")
    assert_true(
        'cookie_secret="12oETzKXQAGaYdkG5gEmGeJJFuYh7EQnp2XdTP1o/Vo="' not in source,
        "facebook.py must not hardcode the Tornado cookie secret",
    )
    assert_true(
        "cookie_secret=options.cookie_secret" in source,
        "Tornado settings must use the configured cookie_secret option",
    )


def test_plan_and_cleanup_contracts_exist():
    assert_true(PLAN.is_file(), "auth contract plan must live under docs/plans")
    plan = PLAN.read_text()
    assert_true("status: completed" in plan, "auth contract plan must be completed")
    assert_true("make check" in plan, "auth contract plan must record verification")

    gitignore = GITIGNORE.read_text()
    for pattern in ["__pycache__/", "*.py[cod]", ".env"]:
        assert_true(pattern in gitignore, ".gitignore must ignore {0}".format(pattern))


def main():
    tests = [
        test_auth_handler_has_no_stray_non_code_suffix,
        test_cookie_secret_comes_from_configuration,
        test_plan_and_cleanup_contracts_exist,
    ]
    for test in tests:
        test()
    print("WillBeOut contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
