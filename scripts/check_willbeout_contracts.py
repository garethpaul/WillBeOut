#!/usr/bin/env python3
"""Static safety contracts for the legacy WillBeOut Tornado app."""
import hashlib
import re
from pathlib import Path

from dependency_lock_contract import (
    EXPECTED_GUIDANCE,
    validate as validate_dependency_lock,
    validate_guidance,
)
from workflow_contract import validate as validate_workflow


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "auth.py"
BASE = ROOT / "base.py"
EVENTS = ROOT / "events.py"
MOBILE = ROOT / "mobile.py"
VOTES = ROOT / "votes.py"
ATTENDEES = ROOT / "attendees.py"
MESSAGES = ROOT / "messages.py"
FACEBOOK = ROOT / "facebook.py"
DATABASE = ROOT / "database.py"
FACEBOOK_CLIENT = ROOT / "facebook_client.py"
SESSION = ROOT / "session.py"
REQUIREMENTS = ROOT / "requirements.txt"
REQUIREMENTS_LOCK = ROOT / "requirements.lock"
MODERN_RUNTIME_PLAN = ROOT / "docs" / "plans" / "2026-06-12-modern-python-web-runtime.md"
OAUTH_ERROR_PLAN = ROOT / "docs" / "plans" / "2026-06-13-oauth-error-callbacks.md"
EVENT_ENDPOINT_ACCESS_PLAN = ROOT / "docs" / "plans" / "2026-06-13-event-scoped-endpoint-authorization.md"
COOKIE_MAX_AGE_PLAN = ROOT / "docs" / "plans" / "2026-06-13-signed-cookie-max-age-enforcement.md"
MAKE_ROOT_PROTECTION_PLAN = ROOT / "docs" / "plans" / "2026-06-14-make-root-override-protection.md"
EVENT_VOTE_USER_PLAN = ROOT / "docs" / "plans" / "2026-06-14-event-vote-user-binding.md"
HASH_VERIFIED_LOCK_PLAN = ROOT / "docs" / "plans" / "2026-06-15-hash-verified-production-lock.md"
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
CI_PLAN = ROOT / "docs" / "plans" / "2026-06-10-ci-baseline.md"
HTTPS_TEMPLATE_PLAN = ROOT / "docs" / "plans" / "2026-06-10-https-template-integrations.md"
SESSION_COOKIE_PLAN = ROOT / "docs" / "plans" / "2026-06-10-session-cookie-hardening.md"
XSRF_PLAN = ROOT / "docs" / "plans" / "2026-06-10-xsrf-write-protection.md"
CODEQL_PLAN = ROOT / "docs" / "plans" / "2026-06-12-willbeout-first-party-codeql-remediation.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"
CODEQL_WORKFLOW = ROOT / ".github" / "workflows" / "codeql.yml"
CODEQL_CONFIG = ROOT / ".github" / "codeql-config.yml"
GITIGNORE = ROOT / ".gitignore"
MAKEFILE = ROOT / "Makefile"
EVENT_TEMPLATE = ROOT / "templates" / "event.html"
BASE_TEMPLATE = ROOT / "templates" / "base.html"
STREAM_TEMPLATE = ROOT / "templates" / "stream.html"
MOBILE_EVENT_TEMPLATE = ROOT / "templates" / "mobile_event.html"
EVENTS_JAVASCRIPT = ROOT / "static" / "js" / "events.js"
VENDORED_BOOTSTRAP = ROOT / "static" / "js" / "bootstrap.js"


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
        "configured_cookie_secret = cookie_secret or options.cookie_secret" in source
        and "cookie_secret=configured_cookie_secret" in source
        and 'raise RuntimeError("COOKIE_SECRET is required")' in source,
        "Tornado settings must require and use the configured cookie secret",
    )


def test_session_cookie_is_http_only_and_secure():
    source = AUTH.read_text()
    base_source = BASE.read_text()
    auth_callback = source.split("class AuthLoginHandler", 1)[1].split("class AuthLogoutHandler", 1)[0]

    assert_true(
        'self.set_secure_cookie(\n            "user"' in auth_callback,
        "auth callback must set the signed user cookie",
    )
    assert_true(
        "httponly=True" in auth_callback,
        "encrypted user cookie must not be readable by browser JavaScript",
    )
    assert_true(
        "secure=True" in auth_callback,
        "encrypted user cookie must only be sent over HTTPS",
    )
    assert_true("samesite=\"Lax\"" in auth_callback, "user cookie must use SameSite=Lax")
    assert_true(
        "USER_COOKIE_MAX_AGE_DAYS = 1" in base_source
        and "expires_days=self.USER_COOKIE_MAX_AGE_DAYS" in auth_callback
        and '"user", max_age_days=self.USER_COOKIE_MAX_AGE_DAYS' in base_source,
        "user cookie set and verification paths must share the one-day lifetime",
    )
    assert_true(
        "OAUTH_COOKIE_MAX_AGE_DAYS = 10 / (24 * 60)" in base_source
        and auth_callback.count("expires_days=self.OAUTH_COOKIE_MAX_AGE_DAYS") == 2
        and auth_callback.count("max_age_days=self.OAUTH_COOKIE_MAX_AGE_DAYS") == 2,
        "OAuth cookie set and verification paths must share the ten-minute lifetime",
    )
    assert_true("session_cipher\"].encrypt_user(user)" in auth_callback, "access tokens must be encrypted before cookie storage")


def test_oauth_error_callbacks_are_state_bound_and_redacted():
    auth_source = AUTH.read_text()
    callback = auth_source.split("class AuthLoginHandler", 1)[1].split(
        "class AuthLogoutHandler", 1
    )[0]
    for contract in [
        'has_code = "code" in self.request.arguments',
        'has_error = "error" in self.request.arguments',
        'self._finish_oauth_error(400, "Invalid OAuth state")',
        "if has_code and has_error:",
        'self._finish_oauth_error(403, "Facebook authorization denied")',
        'self._finish_oauth_error(502, "Facebook authorization failed")',
        'self.clear_cookie("facebook_oauth_state")',
        'self.clear_cookie("facebook_oauth_next")',
    ]:
        assert_true(contract in callback, "OAuth callback must keep {0}".format(contract))
    assert_true(
        callback.index("if not valid_state:")
        < callback.index('self.clear_cookie("facebook_oauth_state")')
        < callback.index("if has_error:"),
        "OAuth callbacks must validate state and clear transient cookies before provider errors",
    )
    assert_true(
        "error_description" not in auth_source,
        "OAuth callback responses must not read or reflect provider descriptions",
    )

    application_source = FACEBOOK.read_text()
    for contract in [
        "def log_request_without_query(handler):",
        "handler.request.path",
        "log_function=log_request_without_query",
    ]:
        assert_true(contract in application_source, "OAuth logging must keep {0}".format(contract))
    assert_true(
        "handler.request.uri" not in application_source,
        "application access logs must not include callback query strings",
    )

    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()
    for test_name in [
        "test_oauth_error_rejects_invalid_state_before_handling",
        "test_oauth_access_denied_clears_state_without_restarting",
        "test_oauth_provider_error_is_stable_and_not_exchanged",
        "test_oauth_callback_rejects_code_and_error_together",
    ]:
        assert_true(test_name in runtime_tests, "runtime coverage must keep {0}".format(test_name))


def test_state_changes_require_post_and_xsrf_tokens():
    application_source = FACEBOOK.read_text()
    assert_true(
        "xsrf_cookies=True" in application_source,
        "Tornado must enforce XSRF checks for unsafe HTTP methods",
    )
    assert_true(
        "xsrf_cookies=False" not in application_source,
        "Tornado XSRF protection must not be disabled",
    )

    mutating_handlers = (
        (ATTENDEES, "Attend", "AttendNo"),
        (ATTENDEES, "AttendNo", "AttendData"),
        (VOTES, "VoteHandler", "ChangeVoteHandler"),
        (VOTES, "ChangeVoteHandler", None),
        (MESSAGES, "DMHandler", "MessageHandler"),
        (AUTH, "AuthLogoutHandler", None),
    )
    for path, class_name, next_class in mutating_handlers:
        source = path.read_text().split("class {0}".format(class_name), 1)[1]
        if next_class:
            source = source.split("class {0}".format(next_class), 1)[0]
        assert_true(
            "def post(self):" in source,
            "{0} mutations must use POST".format(class_name),
        )
        assert_true(
            "def get(self):" not in source,
            "{0} must not mutate state through GET".format(class_name),
        )

    event_template = EVENT_TEMPLATE.read_text()
    base_template = BASE_TEMPLATE.read_text()
    stream_template = STREAM_TEMPLATE.read_text()
    mobile_template = MOBILE_EVENT_TEMPLATE.read_text()
    calendar_javascript = EVENTS_JAVASCRIPT.read_text()

    for forbidden_href in (
        "href='/vote",
        "href='/change/vote",
        "href='/attend",
        'href="/delete/message',
        "href='../auth/logout",
        'href="/auth/logout',
    ):
        assert_true(
            forbidden_href not in event_template + base_template + stream_template,
            "state-changing links must not use GET: {0}".format(forbidden_href),
        )

    assert_true(
        'action="/auth/logout" method="post"' in base_template + stream_template,
        "logout form must use POST",
    )
    assert_true(
        "data-action='/vote'" in event_template
        and "data-action='/change/vote'" in event_template,
        "vote controls must use explicit POST action buttons",
    )
    assert_true(
        base_template.count("{% module xsrf_form_html() %}") >= 1
        and stream_template.count("{% module xsrf_form_html() %}") >= 1
        and mobile_template.count("{% module xsrf_form_html() %}") >= 1,
        "logout and mobile forms must render Tornado XSRF fields",
    )
    assert_true(
        event_template.count("{% raw x %}") >= 2,
        "desktop event forms must include the rendered Tornado XSRF field",
    )
    assert_true(
        event_template.count("getCookie('_xsrf')") >= 3,
        "desktop AJAX mutations must send the XSRF token",
    )
    assert_true(
        mobile_template.count("'_xsrf': getCookie(") >= 2,
        "mobile AJAX mutations must send the XSRF token",
    )
    assert_true(
        '_xsrf: getCookie("_xsrf")' in calendar_javascript,
        "calendar AJAX mutations must send the XSRF token",
    )


def test_auth_next_redirects_are_local_only():
    base_source = BASE.read_text()
    auth_source = AUTH.read_text()

    assert_true("def get_safe_next_url" in base_source, "BaseHandler must expose a safe next-url helper")
    assert_true('next_url == "/"' in base_source, "safe next-url helper must explicitly allow the home path")
    assert_true('next_url == "/events"' in base_source, "safe next-url helper must explicitly allow the events path")
    assert_true("return next_url" not in base_source, "safe next-url helper must return only literal allowlisted paths")
    assert_true(
        'self.redirect(self.get_argument("next"' not in auth_source,
        "auth callback must not redirect directly to a next argument",
    )
    assert_true(
        'self.get_safe_next_url_value(next_url, "/events")' in auth_source,
        "auth callback must redirect through the safe next-url helper",
    )
    assert_true(
        '"facebook_oauth_next"' in auth_source,
        "auth login must bind the sanitized next path to a secure cookie",
    )
    assert_true("hmac.compare_digest" in auth_source, "auth callback must validate OAuth state")
    assert_true("from ismobile import check" not in auth_source, "auth must not use the redundant mobile detector")
    assert_true("check(user_agent)" not in auth_source, "auth must not evaluate the legacy mobile regex")
    assert_true(not (ROOT / "ismobile.py").exists(), "the unused high-cost mobile detector must remain removed")

    for template_path in [ROOT / "templates" / "index.html", ROOT / "templates" / "mobile_index.html"]:
        assert_true(
            'href="/auth/login?next=/events"' in template_path.read_text(),
            "login links must request the literal /events destination",
        )


def test_event_rendering_requires_owner_or_friend_access():
    source = EVENTS.read_text()
    assert_true(
        "self.event = await self.require_event_access(_eventid)" in source,
        "desktop EventHandler must use the shared event access guard",
    )
    assert_true(
        source.index("await self.require_event_access(_eventid)") < source.index("self.suggest = self.db.query"),
        "EventHandler must enforce access before rendering event.html",
    )


def test_event_page_binds_authenticated_user_to_vote_query():
    source = EVENTS.read_text()
    base_template = BASE_TEMPLATE.read_text()
    event_template = EVENT_TEMPLATE.read_text()
    handler = source.split("class EventHandler", 1)[1].split("class EventsHandler", 1)[0]
    access_guard = "self.event = await self.require_event_access(_eventid)"
    user_binding = "_user_id = self.get_current_user()['id']"
    vote_query = '""", _eventid, int(_user_id))'

    assert_true(user_binding in handler, "EventHandler must bind the authenticated user id")
    assert_true(vote_query in handler, "EventHandler vote query must use the bound user id")
    assert_true(
        handler.index(access_guard) < handler.index(user_binding) < handler.index(vote_query),
        "EventHandler must authorize before binding the vote query user",
    )
    assert_true(
        re.search(r"\b_id\b", handler) is None,
        "EventHandler must not reference an undefined standalone _id",
    )
    assert_true(
        "current_user['link']" not in base_template,
        "authenticated templates must not require the unavailable Graph link field",
    )
    assert_true(
        "https://www.facebook.com/{{ escape(current_user['id']) }}" in base_template,
        "authenticated profile links must derive from the bound Graph user id",
    )
    for legacy_attribute in ["event.id", "event.place", "event.f", "event.t"]:
        assert_true(
            legacy_attribute not in event_template,
            "event template must use DictCursor-compatible access: " + legacy_attribute,
        )
    assert_true(
        'postToFeed("https://willbeout.com/event?id={{ event[\'id\'] }}"' in event_template,
        "event sharing must use dictionary access for the event id",
    )

    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()
    for contract in [
        "test_owner_event_page_binds_authenticated_user_to_vote_query",
        'self.assertIn("willbeout_votes", vote_statement)',
        "self.assertEqual((1, 42), vote_parameters)",
        "self.assertEqual(200, response.code)",
    ]:
        assert_true(contract in runtime_tests, "runtime tests must preserve vote user binding: " + contract)


def test_all_event_scoped_endpoints_require_shared_access():
    base_source = BASE.read_text()
    assert_true("async def require_event_access(self, event_id):" in base_source, "BaseHandler must centralize event access")
    assert_true("def friendship_visible(streams, owner_id):" in base_source, "BaseHandler must centralize exact friend matching")
    assert_true('"SELECT * FROM willbeout_events WHERE id = %s", event_id' in base_source, "shared access must load the requested event")
    assert_true("raise tornado.web.HTTPError(404)" in base_source, "shared access must return 404 for missing events")
    assert_true('"/me/friends", current_user["access_token"], fields="id", limit=500' in base_source, "shared access must use the authenticated Facebook token")
    assert_true("raise tornado.web.HTTPError(403)" in base_source, "shared access must reject non-owner non-friends")

    required_counts = {
        EVENTS: 3,
        MOBILE: 1,
        ATTENDEES: 3,
        MESSAGES: 3,
        VOTES: 2,
        FACEBOOK: 1,
    }
    for path, expected_count in required_counts.items():
        actual_count = path.read_text().count("await self.require_event_access(")
        assert_true(
            actual_count == expected_count,
            "{0} must guard all event-scoped methods ({1} expected, {2} found)".format(
                path.name, expected_count, actual_count
            ),
        )

    message_source = MESSAGES.read_text()
    assert_true(
        "DELETE FROM willbeout_messages WHERE id = %s AND user_id = %s AND event_id = %s" in message_source,
        "message deletion must bind the mutated row to the authorized event",
    )

    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()
    for contract in [
        "test_unauthorized_event_reads_stop_after_access_lookup",
        "test_unauthorized_event_writes_stop_before_mutation",
        "test_owner_access_skips_facebook_and_reaches_event_data",
        "test_friend_access_reaches_authorized_mutation",
        "test_missing_event_is_not_disclosed_as_forbidden",
        "self.assertEqual([], self.database.execute_calls, path)",
        "self.assertEqual([], self.database.query_calls, path)",
    ]:
        assert_true(contract in runtime_tests, "runtime tests must preserve event access contract: " + contract)


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
    assert_true(
        "self.event = await self.require_event_access(_eventid)" in source
        and source.index("await self.require_event_access(_eventid)") < source.index("self.places = self.db.query"),
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


def test_active_template_integrations_use_https():
    checked_paths = [
        ROOT / "templates" / "base.html",
        ROOT / "templates" / "event.html",
        ROOT / "templates" / "events.html",
        ROOT / "templates" / "feedit.html",
        ROOT / "templates" / "mobile_event.html",
        ROOT / "templates" / "mobile_events.html",
        ROOT / "templates" / "mobile_index.html",
        ROOT / "templates" / "modules" / "post.html",
    ]
    combined = "\n".join(path.read_text() for path in checked_paths)

    for prefix in [
        "http://code.jquery.com",
        "http://connect.facebook.net",
        "http://api.yelp.com",
        "http://www.facebook.com/profile.php",
        "http://willbeout.com/event",
        "http://127.0.0.1:5000/event",
    ]:
        assert_true(prefix not in combined, "active template integration must use HTTPS: {0}".format(prefix))

    for expected in [
        "https://code.jquery.com/jquery-1.7.1.min.js",
        "https://code.jquery.com/mobile/1.1.1/jquery.mobile-1.1.1.min.css",
        "https://code.jquery.com/mobile/1.1.1/jquery.mobile-1.1.1.min.js",
        "https://connect.facebook.net/en_US/all.js",
        "https://api.yelp.com/business_review_search?",
        "https://www.facebook.com/profile.php?id=",
        "https://willbeout.com/event?id=",
    ]:
        assert_true(expected in combined, "active template integration must stay on HTTPS: {0}".format(expected))


def test_fixed_cdn_resources_use_reviewed_integrity():
    expected = {
        "https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js": (
            "sha384-SDFvKZaD/OapoAVqhWJM8vThqq+NQWczamziIoxiMYVNrVeUUrf2zhbsFvuHOrAh",
            3,
        ),
        "https://code.jquery.com/jquery-1.7.1.min.js": (
            "sha384-npxfGiG5C/F5X72RqcKFYSfzr1AXsDiu1YC/ydsOrS+jL554Jh4zFAx9GpQi4lXQ",
            3,
        ),
        "https://code.jquery.com/mobile/1.1.1/jquery.mobile-1.1.1.min.css": (
            "sha384-31ymrrslLx0ofx2q0EHCjIS4EP7kb0vHWi50Seb913TPXArCPyCsfuH5FnNkFWt3",
            3,
        ),
        "https://code.jquery.com/mobile/1.1.1/jquery.mobile-1.1.1.min.js": (
            "sha384-t8aBsXwe6RT0fl56nhrEIGVQMFx4cLjxUzir5ez5nuk4WoLAk1Lov2O3H+jGrT+Y",
            3,
        ),
    }
    template_source = "\n".join(path.read_text() for path in (ROOT / "templates").glob("*.html"))
    resource_tags = re.findall(
        r'<(?:script|link)\b[^>]*(?:src|href)="(https://(?:ajax\.googleapis\.com|code\.jquery\.com)/[^\"]+)"[^>]*>',
        template_source,
    )
    assert_true(len(resource_tags) == 12, "fixed CDN resource inventory must contain exactly twelve reviewed tags")
    for resource_url, (integrity, expected_count) in expected.items():
        matching_tags = re.findall(
            r'<(?:script|link)\b[^>]*(?:src|href)="{0}"[^>]*>'.format(re.escape(resource_url)),
            template_source,
        )
        assert_true(len(matching_tags) == expected_count, "unexpected fixed CDN resource count: {0}".format(resource_url))
        for tag in matching_tags:
            assert_true('integrity="{0}"'.format(integrity) in tag, "fixed CDN resource hash drift: {0}".format(resource_url))
            assert_true('crossorigin="anonymous"' in tag, "fixed CDN resource must use anonymous CORS: {0}".format(resource_url))


def test_codeql_analyzes_first_party_sources_only():
    workflow = CODEQL_WORKFLOW.read_text()
    config = CODEQL_CONFIG.read_text()
    expected_actions = [
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "github/codeql-action/init@8aad20d150bbac5944a9f9d289da16a4b0d87c1e",
        "github/codeql-action/analyze@8aad20d150bbac5944a9f9d289da16a4b0d87c1e",
    ]
    actions = re.findall(r"^\s*uses:\s*([^\s#]+)", workflow, re.MULTILINE)

    for contract in [
        "security-events: write",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "language: [actions, python, javascript-typescript]",
        "build-mode: none",
        "config-file: ./.github/codeql-config.yml",
        "persist-credentials: false",
        "schedule:",
        "workflow_dispatch:",
        "cancel-in-progress: true",
    ]:
        assert_true(contract in workflow, "CodeQL must keep contract: {0}".format(contract))
    assert_true(actions == expected_actions, "CodeQL must use only reviewed immutable actions")
    assert_true("pull_request_target" not in workflow, "CodeQL must not use privileged pull-request execution")
    assert_true(config == "paths-ignore:\n  - static/js/bootstrap.js\n", "CodeQL exclusion must remain limited to vendored Bootstrap")
    assert_true(not (ROOT / "static" / "js" / "bootstrap.min.js").exists(), "unused duplicate Bootstrap bundle must remain removed")

    vendor_source = VENDORED_BOOTSTRAP.read_bytes()
    assert_true(b"bootstrap-transition.js v2.1.0" in vendor_source, "vendored Bootstrap version header must remain explicit")
    assert_true(b"Licensed under the Apache License, Version 2.0" in vendor_source, "vendored Bootstrap license header must remain explicit")
    assert_true(
        hashlib.sha256(vendor_source).hexdigest() == "192b8b38dda340e751ab5b5272a5f783b45ff76c698642bec552f0e2ddd70fce",
        "vendored Bootstrap checksum changed without reviewed analysis scope",
    )
    workflow_inventory = sorted(path.name for path in (ROOT / ".github" / "workflows").glob("*.yml"))
    assert_true(workflow_inventory == ["check.yml", "codeql.yml"], "workflow inventory must contain only Check and CodeQL")


def test_ci_workflow_runs_make_check():
    assert_true(CI_WORKFLOW.is_file(), "GitHub Actions check workflow must exist")
    workflow = CI_WORKFLOW.read_text()
    errors = validate_workflow(workflow)
    assert_true(not errors, "CI workflow must {0}".format(errors[0]) if errors else "")

    readme = (ROOT / "README.md").read_text()
    assert_true("GitHub Actions" in readme, "README must document the GitHub Actions check")
    makefile = (ROOT / "Makefile").read_text()
    assert_true("test_modern_runtime.py" in makefile, "Makefile must run executable modern runtime tests")
    assert_true("PYTHON2" not in makefile, "Makefile must not retain the retired Python 2 path")
    assert_true("WORKFLOW_CONTRACT_SCRIPT" in makefile, "Makefile must run workflow mutations")


def test_modern_runtime_dependency_and_api_contracts():
    requirements = REQUIREMENTS.read_text()
    lock = REQUIREMENTS_LOCK.read_text()
    errors = validate_dependency_lock(requirements, lock)
    assert_true(not errors, "dependency lock must {0}".format(errors[0]) if errors else "")
    guidance = {path: (ROOT / path).read_text() for path in EXPECTED_GUIDANCE}
    guidance_errors = validate_guidance(guidance)
    assert_true(not guidance_errors, "dependency guidance must {0}".format(guidance_errors[0]) if guidance_errors else "")
    combined = "\n".join(path.read_text() for path in ROOT.glob("*.py"))
    for retired in [
        "tornado.database",
        "FacebookGraphMixin",
        "tornado.web.asynchronous",
        "MySQLdb",
        "urllib.unquote",
        "urllib.quote",
    ]:
        assert_true(retired not in combined, "first-party sources must not restore retired API {0}".format(retired))

    database_source = DATABASE.read_text()
    for contract in [
        "cursor.execute(statement, parameters)",
        "connection.rollback()",
        "connection.close()",
        "pymysql.cursors.DictCursor",
    ]:
        assert_true(contract in database_source, "database adapter must keep {0}".format(contract))

    graph_source = FACEBOOK_CLIENT.read_text()
    for contract in [
        '"https://www.facebook.com/{}/dialog/oauth?{}"',
        '"https://graph.facebook.com/{}/oauth/access_token"',
        'headers={"Authorization": "Bearer " + access_token}',
        "request_timeout=self.timeout",
        "connect_timeout=self.timeout",
        "follow_redirects=False",
        "self.http_client.fetch(request, max_body_size=1024 * 1024)",
        'FacebookClientError("Facebook request failed")',
    ]:
        assert_true(contract in graph_source, "Facebook client must keep {0}".format(contract))
    assert_true("response.body" not in graph_source.split("raise FacebookClientError", 1)[-1], "Facebook errors must not expose response bodies")

    session_source = SESSION.read_text()
    for contract in ["Fernet", "InvalidToken", "SESSION_ENCRYPTION_KEY is required", "return None"]:
        assert_true(contract in session_source, "session encryption must keep {0}".format(contract))

    application_source = FACEBOOK.read_text()
    for contract in [
        'raise RuntimeError("FACEBOOK_REDIRECT_URI must use HTTPS")',
        'autoescape="xhtml_escape"',
        "facebook_redirect_uri=configured_redirect_uri",
    ]:
        assert_true(contract in application_source, "application must keep {0}".format(contract))
    for template in [EVENT_TEMPLATE, ROOT / "templates" / "events.html"]:
        assert_true("{% raw x %}" in template.read_text(), "XSRF markup must remain explicitly raw under autoescaping")

    workflow = CI_WORKFLOW.read_text()
    for contract in [
        "python -m pip install --disable-pip-version-check --require-hashes -r requirements.lock",
        "dependency-audit:",
        "pip-audit==2.10.0",
        "pip-audit -r requirements.lock",
    ]:
        assert_true(contract in workflow, "CI workflow must keep {0}".format(contract))
    assert_true(workflow.count("persist-credentials: false") == 2, "both workflow jobs must disable persisted credentials")

    assert_true(HASH_VERIFIED_LOCK_PLAN.is_file(), "hash lock plan must remain tracked")

    plan = MODERN_RUNTIME_PLAN.read_text()
    assert_true(plan.count("status: completed") == 1, "modern runtime plan must record one completed status")
    assert_true("## Work Completed" in plan, "modern runtime plan must record completed work")
    assert_true("## Verification Completed" in plan, "modern runtime plan must record completed verification")
    assert_true(
        not re.search(r"(?i)\b(?:pending|todo|tbd|not run|remains required)\b", plan),
        "modern runtime plan must not retain unfinished markers",
    )
    for contract in [
        "Tornado 6.5.5",
        "Python 3.12",
        "tornado.database",
        "FacebookGraphMixin",
        "pip-audit",
        "27432092033",
        "27432092095",
        "0c3ce2bda13684c1d6c4cdac69ca15223263766d",
        "zero annotations",
        "OPEN, CLEAN, and MERGEABLE",
        "push` to\n  `master`",
    ]:
        assert_true(contract in plan, "modern runtime plan must record {0}".format(contract))


def test_makefile_is_root_independent():
    makefile = MAKEFILE.read_text()
    makefile_lines = set(makefile.splitlines())

    assert_true(
        "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile_lines,
        "Makefile must protect the repository root",
    )
    assert_true("PYTHON ?= python3" in makefile_lines, "Makefile must preserve the Python command override")
    assert_true(
        '\tfind "$(ROOT)" -type f \\( -name \'*.pyc\' -o -name \'*.pyo\' \\) -delete' in makefile_lines,
        "Makefile cleanup must remove Python bytecode from the repository root",
    )
    assert_true(
        '\tfind "$(ROOT)" -type d -name \'__pycache__\' -prune -exec rm -rf {} +' in makefile_lines,
        "Makefile cleanup must remove Python cache directories from the repository root",
    )
    assert_true(
        "CHECK_SCRIPT := $(ROOT)/scripts/check_willbeout_contracts.py" in makefile,
        "Makefile must use the rooted checker path",
    )
    assert_true(
        '$(MAKE) -f "$(ROOT)/Makefile" clean' in makefile,
        "recursive cleanup must use the rooted Makefile",
    )
    assert_true(
        'cd "$(ROOT)" && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest -v test_modern_runtime.py'
        in makefile,
        "runtime tests must execute from the repository root",
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
    assert_completed_plan(CI_PLAN, "CI baseline")
    assert_completed_plan(HTTPS_TEMPLATE_PLAN, "HTTPS template integrations")
    assert_completed_plan(SESSION_COOKIE_PLAN, "session cookie hardening")
    assert_completed_plan(XSRF_PLAN, "XSRF write protection")
    assert_completed_plan(CODEQL_PLAN, "first-party CodeQL remediation")
    assert_completed_plan(OAUTH_ERROR_PLAN, "OAuth error callbacks")
    assert_completed_plan(EVENT_ENDPOINT_ACCESS_PLAN, "event-scoped endpoint authorization")
    assert_completed_plan(COOKIE_MAX_AGE_PLAN, "signed cookie max-age enforcement")
    assert_completed_plan(MAKE_ROOT_PROTECTION_PLAN, "Make root override protection")
    assert_completed_plan(EVENT_VOTE_USER_PLAN, "event vote user binding")

    gitignore = GITIGNORE.read_text()
    for pattern in ["__pycache__/", "*.py[cod]", ".env", ".DS_Store"]:
        assert_true(pattern in gitignore, ".gitignore must ignore {0}".format(pattern))


def main():
    tests = [
        test_auth_handler_has_no_stray_non_code_suffix,
        test_cookie_secret_comes_from_configuration,
        test_session_cookie_is_http_only_and_secure,
        test_oauth_error_callbacks_are_state_bound_and_redacted,
        test_state_changes_require_post_and_xsrf_tokens,
        test_auth_next_redirects_are_local_only,
        test_event_rendering_requires_owner_or_friend_access,
        test_event_page_binds_authenticated_user_to_vote_query,
        test_all_event_scoped_endpoints_require_shared_access,
        test_event_ids_are_validated_before_database_queries,
        test_vote_ids_are_validated_before_database_writes,
        test_attendee_event_ids_are_validated_before_database_access,
        test_availability_event_ids_are_validated_before_database_access,
        test_message_ids_are_validated_before_database_access,
        test_mobile_event_rendering_requires_owner_or_friend_access,
        test_generated_macos_metadata_is_not_committed,
        test_active_template_integrations_use_https,
        test_fixed_cdn_resources_use_reviewed_integrity,
        test_codeql_analyzes_first_party_sources_only,
        test_ci_workflow_runs_make_check,
        test_modern_runtime_dependency_and_api_contracts,
        test_makefile_is_root_independent,
        test_plan_and_cleanup_contracts_exist,
    ]
    for test in tests:
        test()
    print("WillBeOut contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
