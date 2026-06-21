#!/usr/bin/env python3
"""Static safety contracts for the legacy WillBeOut Tornado app."""
import ast
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
VOTE_SUGGESTION_BINDING_PLAN = ROOT / "docs" / "plans" / "2026-06-16-vote-suggestion-event-binding.md"
TORNADO_SECURITY_UPDATE_PLAN = ROOT / "docs" / "plans" / "2026-06-16-tornado-6.5.7-security-update.md"
AVAILABILITY_PAYLOAD_PLAN = ROOT / "docs" / "plans" / "2026-06-16-availability-payload-validation.md"
AVAILABILITY_TRANSACTION_PLAN = ROOT / "docs" / "plans" / "2026-06-17-availability-replacement-transaction.md"
MAKE_AUTHORITY_PLAN = ROOT / "docs" / "plans" / "2026-06-21-make-authority-isolation.md"
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
MAKE_AUTHORITY_SCRIPT = ROOT / "scripts" / "test-makefile-root.sh"
EVENT_TEMPLATE = ROOT / "templates" / "event.html"
EVENTS_TEMPLATE = ROOT / "templates" / "events.html"
BASE_TEMPLATE = ROOT / "templates" / "base.html"
STREAM_TEMPLATE = ROOT / "templates" / "stream.html"
MOBILE_EVENT_TEMPLATE = ROOT / "templates" / "mobile_event.html"
EVENTS_JAVASCRIPT = ROOT / "static" / "js" / "events.js"
FEEDS_JAVASCRIPT = ROOT / "static" / "js" / "feeds.js"
VENDORED_BOOTSTRAP = ROOT / "static" / "js" / "bootstrap.js"


def assert_true(condition, label):
    if not condition:
        raise AssertionError(label)


def registered_contract_tests():
    tree = ast.parse(Path(__file__).read_text())
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for statement in node.body:
                if (
                    isinstance(statement, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "tests" for target in statement.targets)
                    and isinstance(statement.value, (ast.List, ast.Tuple))
                ):
                    return {
                        element.id for element in statement.value.elts if isinstance(element, ast.Name)
                    }
    return set()


def has_literal_cookie_secret(source):
    tree = ast.parse(source)

    def is_static_string(node, assignments, before_line, resolving=()):
        if isinstance(node, ast.Constant):
            return isinstance(node.value, (str, bytes))
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return is_static_string(node.left, assignments, before_line, resolving) and is_static_string(
                node.right, assignments, before_line, resolving
            )
        if isinstance(node, ast.JoinedStr):
            return all(
                isinstance(value, ast.Constant)
                or (
                    isinstance(value, ast.FormattedValue)
                    and is_static_string(value.value, assignments, before_line, resolving)
                )
                for value in node.values
            )
        if isinstance(node, ast.Name) and node.id not in resolving:
            prior = [
                (line, value)
                for line, value in assignments.get(node.id, ())
                if line < before_line
            ]
            if prior:
                line, value = max(prior, key=lambda item: item[0])
                return is_static_string(value, assignments, line, resolving + (node.id,))
        return False

    class ScopeCollector(ast.NodeVisitor):
        def __init__(self):
            self.assignments = {}
            self.cookie_keywords = []

        def record_assignment(self, target, value, line):
            if isinstance(target, ast.Name):
                self.assignments.setdefault(target.id, []).append((line, value))

        def visit_Assign(self, node):
            for target in node.targets:
                self.record_assignment(target, node.value, node.lineno)
            self.visit(node.value)

        def visit_AnnAssign(self, node):
            if node.value is not None:
                self.record_assignment(node.target, node.value, node.lineno)
                self.visit(node.value)

        def visit_Call(self, node):
            self.cookie_keywords.extend(
                keyword for keyword in node.keywords if keyword.arg == "cookie_secret"
            )
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            return

        def visit_AsyncFunctionDef(self, node):
            return

        def visit_ClassDef(self, node):
            return

        def visit_Lambda(self, node):
            return

    scopes = [tree]
    scopes.extend(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    for scope in scopes:
        collector = ScopeCollector()
        for statement in scope.body:
            collector.visit(statement)
        if any(
            is_static_string(keyword.value, collector.assignments, keyword.lineno)
            for keyword in collector.cookie_keywords
        ):
            return True
    return False


def test_auth_handler_has_no_stray_non_code_suffix():
    source = AUTH.read_text()
    assert_true("åå" not in source, "auth.py must not contain stray non-code suffixes")


def test_cookie_secret_comes_from_configuration():
    source = FACEBOOK.read_text()
    synthetic_fixture = "Application({}={})".format("cookie_" + "secret", '"synthetic-value"')
    reassignment_fixture = """
configured_cookie_secret = cookie_secret or options.cookie_secret
configured_cookie_secret = f"synthetic-value"
Application(cookie_secret=configured_cookie_secret)
"""
    propagation_fixture = """
literal_value = "synthetic-value"
intermediate_value = literal_value
Application(cookie_secret=intermediate_value)
"""
    assert_true(
        has_literal_cookie_secret(synthetic_fixture),
        "cookie secret contract fixture must exercise a literal setting",
    )
    assert_true(
        has_literal_cookie_secret(reassignment_fixture),
        "cookie secret contract must follow a static reassignment into the application setting",
    )
    assert_true(
        has_literal_cookie_secret(propagation_fixture),
        "cookie secret contract must follow static name propagation into the application setting",
    )
    assert_true(
        not has_literal_cookie_secret(source),
        "facebook.py must not contain a literal Tornado cookie secret",
    )
    assert_true("COOKIE_SECRET" in source, "facebook.py must read COOKIE_SECRET from configuration")
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
        'data-link="https://willbeout.com/event?event_id={{ event[\'id\'] }}"' in event_template,
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


def test_vote_suggestions_are_bound_to_events_before_writes():
    base_source = BASE.read_text()
    votes_source = VOTES.read_text()
    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()

    assert_true(
        "def require_event_suggestion(self, suggestion_id, event_id):" in base_source,
        "BaseHandler must expose a shared suggestion/event binding guard",
    )
    assert_true(
        '"SELECT id FROM willbeout_suggest WHERE id = %s AND event_id = %s"' in base_source
        and "            suggestion_id,\n            event_id,\n" in base_source,
        "suggestion binding must query the exact suggestion and event IDs",
    )
    assert_true(
        "if not suggestion:" in base_source and "raise tornado.web.HTTPError(404)" in base_source,
        "missing or cross-event suggestions must fail closed with 404",
    )
    assert_true(
        votes_source.count("self.require_event_suggestion(_suggestion_id, _event_id)") == 2,
        "both vote mutation handlers must bind the suggestion to the authorized event",
    )
    events_source = EVENTS.read_text()
    assert_true(
        "a.id = b.suggestion_id AND a.event_id = b.event_id" in events_source,
        "event vote totals must join votes by both suggestion and event ID",
    )
    for class_name, end_name in (
        ("VoteHandler", "ChangeVoteHandler"),
        ("ChangeVoteHandler", None),
    ):
        handler = votes_source.split("class {0}".format(class_name), 1)[1]
        if end_name:
            handler = handler.split("class {0}".format(end_name), 1)[0]
        access = handler.index("await self.require_event_access(_event_id)")
        binding = handler.index("self.require_event_suggestion(_suggestion_id, _event_id)")
        write_candidates = [
            position for position in (
                handler.find("self.db.execute_rowcount("),
                handler.find("self.db.execute("),
            ) if position >= 0
        ]
        assert_true(
            access < binding < min(write_candidates),
            "{0} must bind the suggestion after event access and before vote storage".format(class_name),
        )
    for test_name in (
        "test_vote_mutations_reject_suggestion_outside_authorized_event",
        "test_vote_mutations_accept_suggestion_bound_to_authorized_event",
    ):
        assert_true(test_name in runtime_tests, "runtime coverage is missing {0}".format(test_name))
    assert_true(
        'self.assertIn("a.event_id = b.event_id", suggestion_statement)' in runtime_tests,
        "runtime event-page coverage must enforce event-scoped vote aggregation",
    )
    assert_true(
        "test_vote_suggestions_are_bound_to_events_before_writes" in registered_contract_tests(),
        "vote suggestion binding contract must remain registered",
    )
    documentation = {
        "README.md": "Votes require the suggestion to belong to the authorized event",
        "SECURITY.md": "Vote mutations also require an exact suggestion and event match",
        "VISION.md": "Bind vote suggestions to the authorized event before storage",
        "CHANGES.md": "Blocked cross-event vote creation and deletion",
    }
    for relative_path, phrase in documentation.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(),
            "{0} must document vote suggestion event binding".format(relative_path),
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


def test_availability_payload_is_validated_before_mutation():
    source = EVENTS.read_text()
    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()
    time_handler_source = source[source.index("class TimeHandler"):]

    assert_true(
        "def parse_available_times(value):" in time_handler_source,
        "availability handler must expose complete-payload parsing",
    )
    assert_true(
        "tokens = unquote(value).split(',')" in time_handler_source,
        "availability parsing must decode and split the complete payload",
    )
    assert_true(
        'if value == "":\n                return []' in time_handler_source,
        "empty availability payloads must represent an intentional clear",
    )
    assert_true(
        "if any(not token for token in tokens):" in time_handler_source,
        "availability parsing must reject empty tokens",
    )
    assert_true(
        "times = [int(token) for token in tokens]" in time_handler_source,
        "availability parsing must convert every token before returning",
    )
    assert_true(
        "len(times) != len(set(times))" in time_handler_source
        and "any(time < 9 or time > 24 for time in times)" in time_handler_source,
        "availability parsing must reject duplicates and times outside the rendered range",
    )
    assert_true(
        "except (TypeError, ValueError):" in time_handler_source
        and "raise tornado.web.HTTPError(400)" in time_handler_source,
        "malformed availability payloads must fail with HTTP 400",
    )
    parse_call = time_handler_source.index(
        "_times = self.parse_available_times(self.get_argument('availabletimes'))"
    )
    transaction_call = time_handler_source.index(
        'self.db.execute_transaction("willbeout_availability", statements)'
    )
    assert_true(
        parse_call < transaction_call,
        "all availability tokens must be valid before replacement starts",
    )
    for test_name in (
        "test_availability_rejects_malformed_payload_before_mutation",
        "test_availability_rejects_duplicate_or_out_of_range_times",
        "test_empty_availability_atomically_clears_existing_times",
        "test_availability_validates_all_times_before_ordered_replacement",
    ):
        assert_true(test_name in runtime_tests, "runtime coverage is missing {0}".format(test_name))
    assert_true(
        "test_availability_payload_is_validated_before_mutation" in registered_contract_tests(),
        "availability payload contract must remain registered",
    )
    documentation = {
        "README.md": "Availability replacements validate every submitted time before deleting saved values",
        "SECURITY.md": "Availability replacements validate the complete payload before the first database mutation",
        "VISION.md": "Validate complete availability payloads before replacing saved values",
        "CHANGES.md": "Validated complete availability payloads before deleting or inserting saved times",
    }
    for relative_path, phrase in documentation.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(),
            "{0} must document availability payload validation".format(relative_path),
        )


def test_availability_selection_updates_payload_after_deselect():
    event_template = EVENT_TEMPLATE.read_text()
    assert_true(
        "at.splice(at.indexOf(_id), 1);" in event_template,
        "availability deselection must remove only the selected time",
    )
    assert_true(
        event_template.count("$('#availabletimes').val(at.join(','));") == 2,
        "availability selection and deselection must both refresh the submitted payload",
    )


def test_event_template_keeps_user_text_out_of_executable_javascript():
    event_template = EVENT_TEMPLATE.read_text()
    events_template = EVENTS_TEMPLATE.read_text()
    base_template = BASE_TEMPLATE.read_text()
    feeds_javascript = FEEDS_JAVASCRIPT.read_text()
    assert_true(
        "onclick='postToFeed" not in event_template + events_template,
        "event names must not be interpolated into inline JavaScript",
    )
    assert_true(
        event_template.count('class="btn-auth btn-facebook share-event"') == 1
        and events_template.count('class="btn-auth btn-facebook share-event"') == 1
        and "$('.share-event').click(function(event)" in feeds_javascript
        and "link: link" in feeds_javascript,
        "event sharing must pass escaped data attributes through a fixed handler",
    )
    assert_true(
        "target='_blank' rel='noopener noreferrer'" in event_template,
        "external suggestion links must isolate the opener",
    )
    assert_true(
        base_template.count('static_url("js/feeds.js")') == 1,
        "the share handler script must load exactly once",
    )


def test_availability_replacement_uses_one_transaction():
    database_source = DATABASE.read_text()
    events_source = EVENTS.read_text()
    runtime_tests = (ROOT / "test_modern_runtime.py").read_text()
    time_handler_source = events_source[events_source.index("class TimeHandler"):]

    transaction_method = database_source[database_source.index("def execute_transaction"):]
    metadata_check = transaction_method.index("information_schema.TABLES")
    statement_loop = transaction_method.index("for statement, parameters in statements:")
    commit_call = transaction_method.index("connection.commit()")
    assert_true(
        metadata_check < statement_loop < commit_call,
        "transaction engine validation must precede writes and one final commit",
    )
    assert_true(
        'TRANSACTIONAL_ENGINES = frozenset(("INNODB",))' in database_source,
        "availability writes must require an explicit transactional engine allowlist",
    )
    assert_true(
        'table.get("ENGINE")' in transaction_method
        and "raise TransactionUnavailableError" in transaction_method,
        "missing or unsupported table engines must fail closed",
    )
    assert_true(
        "connection.rollback()" in transaction_method
        and "connection.close()" in transaction_method,
        "transaction failures must roll back and every connection must close",
    )
    failure_block = transaction_method[transaction_method.index("except Exception:"):]
    rollback_call = failure_block.index("connection.rollback()")
    failure_close = failure_block.index("connection.close()")
    original_raise = failure_block.index("\n            raise\n")
    success_close = failure_block.rindex("connection.close()")
    assert_true(
        rollback_call < failure_close < original_raise < success_close,
        "transaction cleanup must preserve the original failure before the success close",
    )
    assert_true(
        transaction_method.count("connection.close()") == 2,
        "transaction connections must close on both failure and success",
    )
    transaction_call = time_handler_source.index(
        'self.db.execute_transaction("willbeout_availability", statements)'
    )
    delete_statement = time_handler_source.index("DELETE FROM willbeout_availability")
    insert_statement = time_handler_source.index("INSERT INTO willbeout_availability")
    assert_true(
        delete_statement < insert_statement < transaction_call,
        "availability replacement must submit one ordered DELETE/INSERT transaction",
    )
    assert_true(
        "self.db.execute(" not in time_handler_source[:time_handler_source.index("async def get(self):")],
        "availability replacement must not retain independently committed writes",
    )
    for test_name in (
        "test_database_commits_ordered_transaction_on_supported_engine",
        "test_database_rejects_nontransactional_engine_before_writes",
        "test_database_rejects_missing_transaction_table_before_writes",
        "test_database_rolls_back_failed_transaction_without_later_writes",
        "test_database_preserves_transaction_error_when_cleanup_fails",
        "test_availability_validates_all_times_before_ordered_replacement",
    ):
        assert_true(test_name in runtime_tests, "runtime coverage is missing {0}".format(test_name))
    assert_true(
        "test_availability_replacement_uses_one_transaction" in registered_contract_tests(),
        "availability transaction contract must remain registered",
    )
    documentation = {
        "README.md": "Availability replacement uses one verified InnoDB transaction",
        "SECURITY.md": "Availability replacement verifies InnoDB before DELETE",
        "VISION.md": "Replace availability atomically on a verified transactional table",
        "CHANGES.md": "Made availability replacement atomic on verified InnoDB storage",
    }
    for relative_path, phrase in documentation.items():
        assert_true(
            phrase in (ROOT / relative_path).read_text(),
            "{0} must document atomic availability replacement".format(relative_path),
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
        "https://willbeout.com/event?event_id=",
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
    assert_true(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/test_workflow_contract.py'" in makefile,
        "Makefile must run rooted workflow mutations",
    )


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

    for contract in (
        ".DEFAULT_GOAL := check",
        ".SECONDEXPANSION:",
        "PYTHON ?= python3",
        "override PYTHON := $(value PYTHON)",
        "override SHELL := /bin/sh",
        "override .SHELLFLAGS := -c",
        "override MAKEFILES :=",
        "ifneq ($(origin MAKEFILE_LIST),file)",
        "export ROOT",
        "root-test::",
        "\t/bin/sh '$(REPOSITORY_ROOT_LITERAL)/scripts/test-makefile-root.sh'",
        "verify:: root-test lint test contract-test build",
    ):
        assert_true(
            contract in makefile_lines,
            "Makefile authority contract is missing {0!r}".format(contract),
        )
    assert_true("MAKEFLAGS must not be overridden" in makefile, "Makefile must reject caller MAKEFLAGS")
    assert_true("MAKEFILES must be empty" in makefile, "Makefile must reject startup files")
    assert_true("MAKEFILE_LIST must not be overridden" in makefile, "Makefile must reject Makefile-list replacement")
    assert_true("PYTHON must be a literal executable path" in makefile, "Makefile must reject Python Make syntax")
    assert_true(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/check_willbeout_contracts.py'" in makefile,
        "Makefile must use the rooted checker path",
    )
    assert_true(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/test_workflow_contract.py'" in makefile,
        "Makefile must use the rooted workflow mutation path",
    )
    assert_true(
        "'$(REPOSITORY_ROOT_LITERAL)/scripts/test_dependency_lock_contract.py'" in makefile,
        "Makefile must use the rooted lock mutation path",
    )
    assert_true(
        "/usr/bin/find '$(REPOSITORY_ROOT_LITERAL)'" in makefile,
        "Makefile cleanup must stay inside the repository",
    )
    assert_true("-I -B" in makefile, "Python gates must ignore ambient startup state")
    assert_true(
        "sys.path.insert(0, path)" in makefile and "test_modern_runtime.py" in makefile,
        "runtime tests must load the reviewed repository explicitly under isolated Python",
    )
    assert_true(
        MAKE_AUTHORITY_SCRIPT.is_file() and MAKE_AUTHORITY_SCRIPT.stat().st_mode & 0o111,
        "Make authority harness must exist and be executable",
    )
    authority_source = MAKE_AUTHORITY_SCRIPT.read_text()
    for contract in (
        "40 target/authority cases",
        "hostile literal Python path",
        "8 raw Make-syntax controls",
        "MAKEFILE_LIST command rejection and safe environment neutralization",
        "2 startup parse-time boundary reproductions",
        "8 later single-colon replacement rejections",
        "8 later double-colon append boundary reproductions",
        "later override fake-shell boundary reproduction",
        "isolated Python startup",
        "MAKE_BIN=${MAKE_BIN:-/usr/bin/make}",
        "cleanup containment",
        "10 mode rejections",
    ):
        assert_true(
            contract in authority_source,
            "Make authority harness must retain {0}".format(contract),
        )
    docs_text = "\n".join(
        (ROOT / path).read_text()
        for path in (
            "README.md",
            "SECURITY.md",
            "AGENTS.md",
            "CHANGES.md",
            "docs/plans/2026-06-21-make-authority-isolation.md",
        )
    )
    for phrase in (
        "Caller-supplied later makefiles, including double-colon public recipes and later override directives, are outside the local Make trust boundary.",
        "Startup makefiles can run parse-time Make functions before the repository Makefile rejects them.",
        "Documented caller-supplied later makefiles, later override directives, and startup parse-time Make code as outside the local Make trust boundary.",
    ):
        assert_true(phrase in docs_text, "Make boundary documentation must include {0!r}".format(phrase))


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
    assert_completed_plan(VOTE_SUGGESTION_BINDING_PLAN, "vote suggestion event binding")
    assert_completed_plan(TORNADO_SECURITY_UPDATE_PLAN, "Tornado 6.5.7 security update")
    assert_completed_plan(AVAILABILITY_PAYLOAD_PLAN, "availability payload validation")
    assert_completed_plan(AVAILABILITY_TRANSACTION_PLAN, "availability replacement transaction")
    assert_completed_plan(MAKE_AUTHORITY_PLAN, "Make authority isolation")

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
        test_vote_suggestions_are_bound_to_events_before_writes,
        test_attendee_event_ids_are_validated_before_database_access,
        test_availability_event_ids_are_validated_before_database_access,
        test_availability_payload_is_validated_before_mutation,
        test_availability_selection_updates_payload_after_deselect,
        test_event_template_keeps_user_text_out_of_executable_javascript,
        test_availability_replacement_uses_one_transaction,
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
