#!/usr/bin/env python3
"""Static safety contracts for the legacy WillBeOut Tornado app."""
import hashlib
import re
from pathlib import Path

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
        "cookie_secret=options.cookie_secret" in source,
        "Tornado settings must use the configured cookie_secret option",
    )


def test_session_cookie_is_http_only_and_secure():
    source = AUTH.read_text()
    auth_callback = source.split("def _on_auth", 1)[1].split("class AuthLogoutHandler", 1)[0]

    assert_true(
        'self.set_secure_cookie(\n            "user"' in auth_callback,
        "auth callback must set the signed user cookie",
    )
    assert_true(
        "httponly=True" in auth_callback,
        "signed user cookie must not be readable by browser JavaScript",
    )
    assert_true(
        "secure=True" in auth_callback,
        "signed user cookie must only be sent over HTTPS",
    )


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
        event_template.count("{{ x }}") >= 2,
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
        'self.get_safe_next_url("/events")' in auth_source,
        "auth callback must redirect through the safe next-url helper",
    )
    assert_true(
        "tornado.escape.url_escape(next_url)" in auth_source,
        "auth login URL must carry the sanitized next path",
    )
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
    assert_true("Skipping legacy Python 2 syntax checks" in makefile, "Makefile must guard missing Python 2")
    assert_true("WORKFLOW_CONTRACT_SCRIPT" in makefile, "Makefile must run workflow mutations")


def test_makefile_is_root_independent():
    makefile = MAKEFILE.read_text()

    assert_true(
        "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))" in makefile,
        "Makefile must resolve the repository root",
    )
    assert_true(
        "CHECK_SCRIPT := $(ROOT)/scripts/check_willbeout_contracts.py" in makefile,
        "Makefile must use the rooted checker path",
    )
    assert_true(
        '$(MAKE) -f "$(ROOT)/Makefile" clean' in makefile,
        "recursive cleanup must use the rooted Makefile",
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

    gitignore = GITIGNORE.read_text()
    for pattern in ["__pycache__/", "*.py[cod]", ".env", ".DS_Store"]:
        assert_true(pattern in gitignore, ".gitignore must ignore {0}".format(pattern))


def main():
    tests = [
        test_auth_handler_has_no_stray_non_code_suffix,
        test_cookie_secret_comes_from_configuration,
        test_session_cookie_is_http_only_and_secure,
        test_state_changes_require_post_and_xsrf_tokens,
        test_auth_next_redirects_are_local_only,
        test_event_rendering_requires_owner_or_friend_access,
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
        test_makefile_is_root_independent,
        test_plan_and_cleanup_contracts_exist,
    ]
    for test in tests:
        test()
    print("WillBeOut contract checks passed ({0} tests)".format(len(tests)))


if __name__ == "__main__":
    main()
