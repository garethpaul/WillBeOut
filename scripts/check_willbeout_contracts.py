#!/usr/bin/env python3
"""Static safety contracts for the legacy WillBeOut Tornado app."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "auth.py"
BASE = ROOT / "base.py"
EVENTS = ROOT / "events.py"
MOBILE = ROOT / "mobile.py"
VOTES = ROOT / "votes.py"
ATTENDEES = ROOT / "attendees.py"
MESSAGES = ROOT / "messages.py"
FACEBOOK = ROOT / "facebook.py"
COOKIE_SECRET_PLAN = ROOT / "docs" / "plans" / "2026-06-08-cookie-secret-contract.md"
SAFE_NEXT_PLAN = ROOT / "docs" / "plans" / "2026-06-08-safe-auth-next-redirect.md"
EVENT_ACCESS_PLAN = ROOT / "docs" / "plans" / "2026-06-08-event-access-guard.md"
MOBILE_EVENT_ACCESS_PLAN = ROOT / "docs" / "plans" / "2026-06-09-mobile-event-access-guard.md"
DESKTOP_MISSING_EVENT_PLAN = ROOT / "docs" / "plans" / "2026-06-09-desktop-event-missing-guard.md"
EVENT_ID_VALIDATION_PLAN = ROOT / "docs" / "plans" / "2026-06-09-event-id-validation.md"
VOTE_ID_VALIDATION_PLAN = ROOT / "docs" / "plans" / "2026-06-09-vote-id-validation.md"
ATTENDEE_ID_VALIDATION_PLAN = ROOT / "docs" / "plans" / "2026-06-09-attendee-id-validation.md"
AVAILABILITY_EVENT_ID_VALIDATION_PLAN = ROOT / "docs" / "plans" / "2026-06-09-availability-event-id-validation.md"
MESSAGE_ID_VALIDATION_PLAN = ROOT / "docs" / "plans" / "2026-06-09-message-id-validation.md"
GENERATED_MACOS_METADATA_PLAN = ROOT / "docs" / "plans" / "2026-06-09-generated-macos-metadata.md"
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


def test_auth_next_redirects_are_local_only():
    base_source = BASE.read_text()
    auth_source = AUTH.read_text()

    assert_true("def get_safe_next_url" in base_source, "BaseHandler must expose a safe next-url helper")
    assert_true(
        'next_url.startswith("/")' in base_source,
        "safe next-url helper must allow only site-local absolute paths",
    )
    assert_true(
        'not next_url.startswith("//")' in base_source,
        "safe next-url helper must reject protocol-relative redirects",
    )
    assert_true(
        'self.redirect(self.get_argument("next"' not in auth_source,
        "auth callback must not redirect directly to a next argument",
    )
    assert_true(
        'self.get_safe_next_url("/events")' in auth_source,
        "auth callback must redirect through the safe next-url helper",
    )
    assert_true(
        "tornado.escape.url_escape(next_url)" in auth_source,
        "auth login URL must carry the sanitized next path",
    )


def test_event_rendering_requires_owner_or_friend_access():
    source = EVENTS.read_text()
    assert_true("def _friendship_visible" in source, "EventHandler must interpret Facebook friend-check responses")
    assert_true(
        "if not self.event:" in source,
        "EventHandler must check for missing events",
    )
    assert_true(
        "raise tornado.web.HTTPError(404)" in source,
        "EventHandler must return 404 for missing events",
    )
    assert_true(
        source.index("raise tornado.web.HTTPError(404)") < source.index("self.suggest = self.db.query"),
        "EventHandler must reject missing events before querying related suggestions",
    )
    assert_true(
        'self.facebook_request("/me/friends/" + str(self.event[\'userid\'])' in source,
        "EventHandler must keep the Facebook friend visibility check",
    )
    assert_true(
        "if self.access != 1 and not self._friendship_visible(streams):" in source,
        "EventHandler must reject non-owner and non-friend event access",
    )
    assert_true(
        "raise tornado.web.HTTPError(403)" in source,
        "EventHandler must return 403 when event access is not allowed",
    )
    assert_true(
        source.index("raise tornado.web.HTTPError(403)") < source.index("self.render('event.html'"),
        "EventHandler must enforce access before rendering event.html",
    )


def test_event_ids_are_validated_before_database_queries():
    base_source = BASE.read_text()
    events_source = EVENTS.read_text()
    mobile_source = MOBILE.read_text()

    assert_true("def get_int_argument" in base_source, "BaseHandler must expose an integer argument helper")
    assert_true(
        "except (TypeError, ValueError):" in base_source,
        "integer argument helper must handle malformed integer values",
    )
    assert_true(
        "raise tornado.web.HTTPError(400)" in base_source,
        "integer argument helper must reject malformed integer values with 400",
    )
    assert_true(
        "_eventid = self.get_int_argument('event_id')" in events_source,
        "desktop EventHandler must validate the event_id argument before queries",
    )
    assert_true(
        "_eventid = self.get_int_argument('id')" in mobile_source,
        "mobile EventHandler must validate the id argument before queries",
    )
    assert_true(
        "int(_eventid)" not in events_source,
        "desktop EventHandler must not re-cast the validated event id",
    )
    assert_true(
        "int(_eventid)" not in mobile_source,
        "mobile EventHandler must not re-cast the validated event id",
    )


def test_vote_ids_are_validated_before_database_writes():
    source = VOTES.read_text()

    assert_true(
        source.count("_event_id = self.get_int_argument('event_id')") >= 2,
        "vote handlers must validate event_id before database writes",
    )
    assert_true(
        source.count("_suggestion_id = self.get_int_argument('id')") >= 2,
        "vote handlers must validate suggestion id before database writes",
    )
    assert_true(
        "int(_event_id)" not in source,
        "vote handlers must not re-cast validated event ids",
    )
    assert_true(
        "int(_suggestion_id)" not in source,
        "vote handlers must not re-cast validated suggestion ids",
    )


def test_attendee_event_ids_are_validated_before_database_access():
    source = ATTENDEES.read_text()

    assert_true(
        source.count("_event_id = self.get_int_argument('event_id')") >= 3,
        "attendance handlers must validate event_id before database access",
    )
    assert_true(
        "_event_id = self.get_argument('event_id')" not in source,
        "attendance handlers must not use raw event_id arguments",
    )
    assert_true(
        "escape(self.get_argument('event_id'))" not in source,
        "attendance handlers must not rely on escaping instead of integer validation",
    )
    assert_true(
        "from re import escape" not in source,
        "attendees.py must not import unused escape handling",
    )
    assert_true(
        "self.redirect('/event?event_id=' + str(_event_id))" in source,
        "attendance redirect must stringify the validated event id",
    )


def test_availability_event_ids_are_validated_before_database_access():
    source = EVENTS.read_text()
    time_handler_source = source[source.index("class TimeHandler"):]

    assert_true(
        time_handler_source.count("_event_id = self.get_int_argument('event_id')") >= 2,
        "availability handlers must validate event_id before database access",
    )
    assert_true(
        "_event_id = self.get_argument('event_id')" not in time_handler_source,
        "availability handlers must not use raw event_id arguments",
    )
    assert_true(
        "int(_event_id)" not in time_handler_source,
        "availability handlers must not re-cast validated event ids",
    )
    assert_true(
        "self.redirect('/event?event_id=' + str(_event_id))" in time_handler_source,
        "availability update redirect must stringify the validated event id",
    )


def test_message_ids_are_validated_before_database_access():
    source = MESSAGES.read_text()

    assert_true(
        "_message_id = self.get_int_argument('ide')" in source,
        "delete-message handler must validate message ids before database writes",
    )
    assert_true(
        source.count("_event_id = self.get_int_argument('event_id')") >= 2,
        "message handlers must validate event_id before database access",
    )
    assert_true(
        "_event_id = self.get_int_argument('id')" in source,
        "message post handler must validate posted event ids before database writes",
    )
    assert_true(
        "_id = self.get_argument('ide')" not in source,
        "delete-message handler must not use raw message id arguments",
    )
    assert_true(
        "event_id = self.get_argument('event_id')" not in source,
        "message list handler must not use raw event_id arguments",
    )
    assert_true(
        "_event_id = self.get_argument('id')" not in source,
        "message post handler must not use raw event id arguments",
    )
    assert_true(
        "self.redirect('/event?event_id=' + str(_event_id))" in source,
        "message redirects must stringify the validated event id",
    )


def test_mobile_event_rendering_requires_owner_or_friend_access():
    source = MOBILE.read_text()
    assert_true("def _friendship_visible" in source, "mobile EventHandler must interpret Facebook friend-check responses")
    assert_true(
        'self.facebook_request("/me/friends/" + str(self.event[\'userid\'])' in source,
        "mobile EventHandler must keep the Facebook friend visibility check",
    )
    assert_true(
        "if self.access != 1 and not self._friendship_visible(streams):" in source,
        "mobile EventHandler must reject non-owner and non-friend event access",
    )
    assert_true(
        "raise tornado.web.HTTPError(403)" in source,
        "mobile EventHandler must return 403 when event access is not allowed",
    )
    assert_true(
        "raise tornado.web.HTTPError(404)" in source,
        "mobile EventHandler must return 404 for missing events",
    )
    assert_true(
        source.index("raise tornado.web.HTTPError(403)") < source.index("self.render('mobile_event.html'"),
        "mobile EventHandler must enforce access before rendering mobile_event.html",
    )


def test_generated_macos_metadata_is_not_committed():
    offenders = []
    for path in ROOT.rglob(".DS_Store"):
        relative = path.relative_to(ROOT)
        if ".git" not in relative.parts:
            offenders.append(relative.as_posix())

    assert_true(
        not offenders,
        "generated macOS metadata must not be committed: {0}".format(", ".join(offenders)),
    )


def assert_completed_plan(path, label):
    assert_true(path.is_file(), "{0} plan must live under docs/plans".format(label))
    plan = path.read_text()
    assert_true("status: completed" in plan.lower(), "{0} plan must be completed".format(label))
    assert_true("make check" in plan, "{0} plan must record verification".format(label))


def test_plan_and_cleanup_contracts_exist():
    assert_completed_plan(COOKIE_SECRET_PLAN, "auth contract")
    assert_completed_plan(SAFE_NEXT_PLAN, "safe auth next redirect")
    assert_completed_plan(EVENT_ACCESS_PLAN, "event access guard")
    assert_completed_plan(MOBILE_EVENT_ACCESS_PLAN, "mobile event access guard")
    assert_completed_plan(DESKTOP_MISSING_EVENT_PLAN, "desktop missing event guard")
    assert_completed_plan(EVENT_ID_VALIDATION_PLAN, "event id validation")
    assert_completed_plan(VOTE_ID_VALIDATION_PLAN, "vote id validation")
    assert_completed_plan(ATTENDEE_ID_VALIDATION_PLAN, "attendee id validation")
    assert_completed_plan(AVAILABILITY_EVENT_ID_VALIDATION_PLAN, "availability event id validation")
    assert_completed_plan(MESSAGE_ID_VALIDATION_PLAN, "message id validation")
    assert_completed_plan(GENERATED_MACOS_METADATA_PLAN, "generated macOS metadata")

    gitignore = GITIGNORE.read_text()
    for pattern in ["__pycache__/", "*.py[cod]", ".env", ".DS_Store"]:
        assert_true(pattern in gitignore, ".gitignore must ignore {0}".format(pattern))


def main():
    tests = [
        test_auth_handler_has_no_stray_non_code_suffix,
        test_cookie_secret_comes_from_configuration,
        test_auth_next_redirects_are_local_only,
        test_event_rendering_requires_owner_or_friend_access,
        test_event_ids_are_validated_before_database_queries,
        test_vote_ids_are_validated_before_database_writes,
        test_attendee_event_ids_are_validated_before_database_access,
        test_availability_event_ids_are_validated_before_database_access,
        test_message_ids_are_validated_before_database_access,
        test_mobile_event_rendering_requires_owner_or_friend_access,
        test_generated_macos_metadata_is_not_committed,
        test_plan_and_cleanup_contracts_exist,
    ]
    for test in tests:
        test()
    print("WillBeOut contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
