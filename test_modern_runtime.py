import asyncio
import json
import time
import unittest
from http.cookies import SimpleCookie
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlparse

from cryptography.fernet import Fernet
from tornado.httpclient import HTTPClientError
from tornado.testing import AsyncHTTPTestCase
from tornado.web import create_signed_value, decode_signed_value

import base
import database
import facebook
import events
import mobile
from facebook_client import FacebookClient, FacebookClientError
from session import SessionCipher


class FakeCursor:
    def __init__(self, rows=None, row=None, rowcount=1, lastrowid=7, error=None):
        self.rows = rows or []
        self.row = row
        self.rowcount = rowcount
        self.lastrowid = lastrowid
        self.error = error
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, statement, parameters):
        self.executions.append((statement, parameters))
        if self.error:
            raise self.error
        return self.rowcount

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closes += 1


class FakeHTTPClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def fetch(self, request, **options):
        self.requests.append(request)
        self.options = options
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return SimpleNamespace(body=json.dumps(response).encode("utf-8"))


class FakeGraphClient:
    def __init__(self, friends=None):
        self.auth_calls = []
        self.request_calls = []
        self.friends = friends or []

    def authorization_url(self, redirect_uri, state):
        return "https://www.facebook.com/v24.0/dialog/oauth?" + urlencode({
            "redirect_uri": redirect_uri,
            "state": state,
        })

    async def authenticate(self, redirect_uri, code):
        self.auth_calls.append((redirect_uri, code))
        return {"id": "42", "name": "Ada", "access_token": "secret-token"}

    async def request(self, path, access_token, **parameters):
        self.request_calls.append((path, access_token, parameters))
        return {"data": self.friends}


class FakeEventDatabase:
    def __init__(self, event=None, suggestion=None):
        self.event = event
        self.suggestion = suggestion
        self.get_calls = []
        self.query_calls = []
        self.execute_calls = []
        self.rowcount_calls = []

    def reset_protected_calls(self):
        self.query_calls = []
        self.execute_calls = []
        self.rowcount_calls = []

    def get(self, statement, *parameters):
        self.get_calls.append((statement, parameters))
        if "willbeout_suggest" in statement:
            return self.suggestion
        return self.event

    def query(self, statement, *parameters):
        self.query_calls.append((statement, parameters))
        return []

    def execute(self, statement, *parameters):
        self.execute_calls.append((statement, parameters))
        return 1

    def execute_rowcount(self, statement, *parameters):
        self.rowcount_calls.append((statement, parameters))
        return 0


class ModernRuntimeTest(unittest.IsolatedAsyncioTestCase):
    def test_database_parameterizes_and_closes_queries(self):
        cursor = FakeCursor(rows=[{"id": 1}])
        connection = FakeConnection(cursor)
        db = database.Database("db", "app", "user", "secret", connect=lambda **_options: connection)

        self.assertEqual([{"id": 1}], db.query("SELECT * FROM events WHERE id = %s", 1))
        self.assertEqual([("SELECT * FROM events WHERE id = %s", (1,))], cursor.executions)
        self.assertEqual(0, connection.commits)
        self.assertEqual(1, connection.closes)

    def test_database_rolls_back_and_closes_failed_writes(self):
        cursor = FakeCursor(error=RuntimeError("database failed"))
        connection = FakeConnection(cursor)
        db = database.Database("db", "app", "user", "secret", connect=lambda **_options: connection)

        with self.assertRaisesRegex(RuntimeError, "database failed"):
            db.execute("DELETE FROM events WHERE id = %s", 1)
        self.assertEqual(1, connection.rollbacks)
        self.assertEqual(1, connection.closes)

    def test_session_cipher_encrypts_and_rejects_tampering(self):
        cipher = SessionCipher(Fernet.generate_key().decode("ascii"))
        encrypted = cipher.encrypt_user({"id": "1", "name": "Ada", "access_token": "token"})

        self.assertNotIn("token", encrypted)
        self.assertEqual(
            {"id": "1", "name": "Ada", "access_token": "token"},
            cipher.decrypt_user(encrypted),
        )
        replacement = "A" if encrypted[10] != "A" else "B"
        tampered = encrypted[:10] + replacement + encrypted[11:]
        self.assertIsNone(cipher.decrypt_user(tampered))

    async def test_facebook_authentication_uses_post_and_bearer_header(self):
        http = FakeHTTPClient([
            {"access_token": "secret-token"},
            {"id": "42", "name": "Ada"},
        ])
        client = FacebookClient("client", "secret", http_client=http, timeout=4.0)

        user = await client.authenticate("https://example.test/auth/login", "code")

        self.assertEqual("secret-token", user["access_token"])
        token_request, profile_request = http.requests
        self.assertEqual("POST", token_request.method)
        self.assertNotIn("secret-token", token_request.url)
        self.assertEqual("Bearer secret-token", profile_request.headers["Authorization"])
        self.assertEqual(4.0, profile_request.request_timeout)
        self.assertEqual(1024 * 1024, http.options["max_body_size"])

    async def test_facebook_errors_are_redacted(self):
        http = FakeHTTPClient([HTTPClientError(500, message="raw-token-response")])
        client = FacebookClient("client", "secret", http_client=http)

        with self.assertRaisesRegex(FacebookClientError, "Facebook request failed") as error:
            await client.request("/me", "secret-token")
        self.assertNotIn("secret-token", str(error.exception))
        self.assertNotIn("raw-token-response", str(error.exception))

    def test_authorization_url_binds_state_and_local_callback(self):
        client = FacebookClient("client", "secret", http_client=FakeHTTPClient([]))
        url = client.authorization_url("https://example.test/auth/login", "state-value")
        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        self.assertEqual("https", parsed.scheme)
        self.assertEqual("www.facebook.com", parsed.netloc)
        self.assertEqual(["state-value"], query["state"])
        self.assertEqual(["code"], query["response_type"])
        self.assertEqual(["public_profile,user_friends"], query["scope"])

    def test_application_starts_with_injected_clients(self):
        db = object()
        graph = object()
        cipher = SessionCipher(Fernet.generate_key().decode("ascii"))

        application = facebook.Application(
            database=db,
            facebook_client=graph,
            session_cipher=cipher,
            cookie_secret="test-cookie-secret",
            facebook_redirect_uri="https://example.test/auth/login",
        )

        self.assertIs(db, application.settings["database"])
        self.assertIs(graph, application.settings["facebook_client"])
        self.assertIs(cipher, application.settings["session_cipher"])
        self.assertTrue(application.settings["xsrf_cookies"])
        self.assertEqual("/auth/login", application.settings["login_url"])

    def test_friend_visibility_requires_the_exact_owner_id(self):
        payload = {"data": [{"id": "7"}, {"id": "42"}]}

        self.assertTrue(base.BaseHandler.friendship_visible(payload, "42"))
        self.assertFalse(base.BaseHandler.friendship_visible(payload, "99"))


class EventEndpointAuthorizationTest(AsyncHTTPTestCase):
    def get_app(self):
        self.database = FakeEventDatabase({"id": 1, "userid": "7"})
        self.graph = FakeGraphClient()
        self.cipher = SessionCipher(Fernet.generate_key().decode("ascii"))
        app = facebook.Application(
            database=self.database,
            facebook_client=self.graph,
            session_cipher=self.cipher,
            cookie_secret="test-cookie-secret",
            facebook_redirect_uri="https://example.test/auth/login",
        )
        app.settings["xsrf_cookies"] = False
        return app

    def _auth_headers(self):
        encrypted = self.cipher.encrypt_user({
            "id": "42",
            "name": "Ada",
            "access_token": "secret-token",
        })
        signed = create_signed_value(
            "test-cookie-secret", "user", encrypted
        ).decode("ascii")
        return {"Cookie": "user=" + signed}

    def _assert_denied_without_protected_database_access(self, path, method="GET", body=None):
        self.database.reset_protected_calls()
        response = self.fetch(
            path,
            method=method,
            body=body,
            headers=self._auth_headers(),
            follow_redirects=False,
        )
        self.assertEqual(403, response.code, path)
        self.assertEqual([], self.database.query_calls, path)
        self.assertEqual([], self.database.execute_calls, path)
        self.assertEqual([], self.database.rowcount_calls, path)

    def test_unauthorized_event_reads_stop_after_access_lookup(self):
        for path in [
            "/messages?event_id=1",
            "/time?event_id=1",
            "/attend/data?event_id=1",
            "/event?event_id=1",
            "/mobile/event?id=1",
        ]:
            self._assert_denied_without_protected_database_access(path)

    def test_unauthorized_event_writes_stop_before_mutation(self):
        requests = [
            ("/attend", "event_id=1"),
            ("/attend/no", "event_id=1"),
            ("/messages", "id=1&msg=hello&type=message"),
            ("/delete/message", "ide=2&event_id=1"),
            ("/vote", "id=2&event_id=1"),
            ("/change/vote", "id=2&event_id=1"),
            ("/suggest", "event_id=1&name=a&url=b&address=c&city=d"),
            ("/time", "event_id=1&availabletimes=1"),
        ]
        for path, body in requests:
            self._assert_denied_without_protected_database_access(
                path, method="POST", body=body
            )

    def test_owner_access_skips_facebook_and_reaches_event_data(self):
        self.database.event = {"id": 1, "userid": "42"}
        response = self.fetch(
            "/messages?event_id=1", headers=self._auth_headers()
        )

        self.assertEqual(200, response.code)
        self.assertEqual(1, len(self.database.query_calls))
        self.assertEqual([], self.graph.request_calls)

    def test_owner_event_page_binds_authenticated_user_to_vote_query(self):
        self.database.event = {
            "id": 1,
            "userid": "42",
            "place": "Office",
            "f": "2026-06-14 09:00",
            "t": "2026-06-14 17:00",
        }

        response = self.fetch(
            "/event?event_id=1", headers=self._auth_headers()
        )

        self.assertEqual(200, response.code)
        self.assertEqual(2, len(self.database.query_calls))
        suggestion_statement, suggestion_parameters = self.database.query_calls[0]
        self.assertIn("a.event_id = b.event_id", suggestion_statement)
        self.assertEqual((1,), suggestion_parameters)
        vote_statement, vote_parameters = self.database.query_calls[1]
        self.assertIn("willbeout_votes", vote_statement)
        self.assertEqual((1, 42), vote_parameters)
        self.assertEqual([], self.graph.request_calls)

    def test_friend_access_reaches_authorized_mutation(self):
        self.graph.friends = [{"id": "7"}]
        response = self.fetch(
            "/attend",
            method="POST",
            body="event_id=1",
            headers=self._auth_headers(),
            follow_redirects=False,
        )

        self.assertEqual(302, response.code)
        self.assertEqual(1, len(self.database.execute_calls))
        self.assertEqual("/me/friends", self.graph.request_calls[0][0])

    def test_vote_mutations_reject_suggestion_outside_authorized_event(self):
        self.database.event = {"id": 1, "userid": "42"}
        self.database.suggestion = None

        for path in ("/vote", "/change/vote"):
            self.database.reset_protected_calls()
            get_call_count = len(self.database.get_calls)
            response = self.fetch(
                path,
                method="POST",
                body="id=2&event_id=1",
                headers=self._auth_headers(),
                follow_redirects=False,
            )

            self.assertEqual(404, response.code, path)
            self.assertEqual([], self.database.query_calls, path)
            self.assertEqual([], self.database.execute_calls, path)
            self.assertEqual([], self.database.rowcount_calls, path)
            suggestion_statement, suggestion_parameters = self.database.get_calls[get_call_count + 1]
            self.assertIn("willbeout_suggest", suggestion_statement)
            self.assertEqual((2, 1), suggestion_parameters)

    def test_vote_mutations_accept_suggestion_bound_to_authorized_event(self):
        self.database.event = {"id": 1, "userid": "42"}
        self.database.suggestion = {"id": 2, "event_id": 1}

        response = self.fetch(
            "/vote",
            method="POST",
            body="id=2&event_id=1",
            headers=self._auth_headers(),
            follow_redirects=False,
        )
        self.assertEqual(302, response.code)
        self.assertEqual(2, len(self.database.rowcount_calls))

        self.database.reset_protected_calls()
        response = self.fetch(
            "/change/vote",
            method="POST",
            body="id=2&event_id=1",
            headers=self._auth_headers(),
            follow_redirects=False,
        )
        self.assertEqual(302, response.code)
        self.assertEqual(1, len(self.database.execute_calls))

    def test_availability_rejects_malformed_payload_before_mutation(self):
        self.database.event = {"id": 1, "userid": "42"}

        for available_times in ("1,invalid", "1,,2", ""):
            self.database.reset_protected_calls()
            response = self.fetch(
                "/time",
                method="POST",
                body=urlencode({"event_id": 1, "availabletimes": available_times}),
                headers=self._auth_headers(),
                follow_redirects=False,
            )

            self.assertEqual(400, response.code, available_times)
            self.assertEqual([], self.database.execute_calls, available_times)

    def test_availability_validates_all_times_before_ordered_replacement(self):
        self.database.event = {"id": 1, "userid": "42"}

        response = self.fetch(
            "/time",
            method="POST",
            body=urlencode({"event_id": 1, "availabletimes": "2,2,5"}),
            headers=self._auth_headers(),
            follow_redirects=False,
        )

        self.assertEqual(302, response.code)
        self.assertEqual(4, len(self.database.execute_calls))
        delete_statement, delete_parameters = self.database.execute_calls[0]
        self.assertIn("DELETE FROM willbeout_availability", delete_statement)
        self.assertEqual((1, 42), delete_parameters)
        self.assertEqual(
            [
                (42, "Ada", 2, 1),
                (42, "Ada", 2, 1),
                (42, "Ada", 5, 1),
            ],
            [parameters for _statement, parameters in self.database.execute_calls[1:]],
        )

    def test_missing_event_is_not_disclosed_as_forbidden(self):
        self.database.event = None
        response = self.fetch(
            "/messages?event_id=1", headers=self._auth_headers()
        )

        self.assertEqual(404, response.code)
        self.assertEqual([], self.graph.request_calls)
        self.assertEqual([], self.database.query_calls)


class AuthHandlerTest(AsyncHTTPTestCase):
    def get_app(self):
        self.graph = FakeGraphClient()
        self.cipher = SessionCipher(Fernet.generate_key().decode("ascii"))
        return facebook.Application(
            database=object(),
            facebook_client=self.graph,
            session_cipher=self.cipher,
            cookie_secret="test-cookie-secret",
            facebook_redirect_uri="https://example.test/auth/login",
        )

    @staticmethod
    def _cookies(response):
        cookies = SimpleCookie()
        for header in response.headers.get_list("Set-Cookie"):
            cookies.load(header)
        return cookies

    def _start_oauth(self):
        response = self.fetch("/auth/login?next=/events", follow_redirects=False)
        self.assertEqual(302, response.code)
        cookies = self._cookies(response)
        state = parse_qs(urlparse(response.headers["Location"]).query)["state"][0]
        cookie_header = "; ".join(
            "{}={}".format(name, morsel.value) for name, morsel in cookies.items()
        )
        return state, cookie_header

    def test_oauth_state_round_trip_creates_encrypted_session(self):
        state, cookie_header = self._start_oauth()

        callback = self.fetch(
            "/auth/login?code=code&state=" + state,
            headers={"Cookie": cookie_header},
            follow_redirects=False,
        )

        self.assertEqual(302, callback.code)
        self.assertEqual("/events", callback.headers["Location"])
        callback_cookies = self._cookies(callback)
        encrypted_user = decode_signed_value(
            "test-cookie-secret", "user", callback_cookies["user"].value
        ).decode("ascii")
        self.assertNotIn("secret-token", encrypted_user)
        self.assertEqual("secret-token", self.cipher.decrypt_user(encrypted_user)["access_token"])
        self.assertEqual([("https://example.test/auth/login", "code")], self.graph.auth_calls)

    def test_oauth_callback_rejects_invalid_state_before_exchange(self):
        response = self.fetch(
            "/auth/login?code=code&state=invalid",
            follow_redirects=False,
        )

        self.assertEqual(400, response.code)
        self.assertEqual([], self.graph.auth_calls)

    def test_oauth_callback_rejects_expired_state_before_exchange(self):
        expired_clock = lambda: time.time() - (11 * 60)
        state_cookie = create_signed_value(
            "test-cookie-secret", "facebook_oauth_state", "expired-state", clock=expired_clock
        ).decode("ascii")
        next_cookie = create_signed_value(
            "test-cookie-secret", "facebook_oauth_next", "/events", clock=expired_clock
        ).decode("ascii")

        response = self.fetch(
            "/auth/login?code=code&state=expired-state",
            headers={
                "Cookie": "facebook_oauth_state={}; facebook_oauth_next={}".format(
                    state_cookie, next_cookie
                )
            },
            follow_redirects=False,
        )

        self.assertEqual(400, response.code)
        self.assertEqual([], self.graph.auth_calls)

    def test_expired_user_cookie_does_not_authenticate(self):
        encrypted_user = self.cipher.encrypt_user(
            {"id": "42", "name": "Ada", "access_token": "secret-token"}
        )
        expired_cookie = create_signed_value(
            "test-cookie-secret",
            "user",
            encrypted_user,
            clock=lambda: time.time() - (2 * 24 * 60 * 60),
        ).decode("ascii")

        response = self.fetch(
            "/events",
            headers={"Cookie": "user=" + expired_cookie},
            follow_redirects=False,
        )

        self.assertEqual(302, response.code)
        self.assertTrue(response.headers["Location"].startswith("/auth/login?"))

    def test_oauth_error_rejects_invalid_state_before_handling(self):
        response = self.fetch(
            "/auth/login?error=access_denied&state=invalid",
            follow_redirects=False,
        )

        self.assertEqual(400, response.code)
        self.assertEqual([], self.graph.auth_calls)

    def test_oauth_access_denied_clears_state_without_restarting(self):
        state, cookie_header = self._start_oauth()
        with self.assertLogs("tornado.access", level="WARNING") as logs:
            response = self.fetch(
                "/auth/login?error=access_denied&error_description=provider-secret&state=" + state,
                headers={"Cookie": cookie_header},
                follow_redirects=False,
            )

        self.assertEqual(403, response.code)
        self.assertEqual(b"Facebook authorization denied", response.body)
        self.assertNotIn("provider-secret", "\n".join(logs.output))
        self.assertIn("GET /auth/login", "\n".join(logs.output))
        self.assertEqual([], self.graph.auth_calls)
        cookies = self._cookies(response)
        self.assertEqual("", cookies["facebook_oauth_state"].value)
        self.assertEqual("", cookies["facebook_oauth_next"].value)
        self.assertNotIn("Location", response.headers)

    def test_oauth_provider_error_is_stable_and_not_exchanged(self):
        state, cookie_header = self._start_oauth()
        with self.assertLogs("tornado.access", level="ERROR") as logs:
            response = self.fetch(
                "/auth/login?error=server_error&error_description=provider-secret&state=" + state,
                headers={"Cookie": cookie_header},
                follow_redirects=False,
            )

        self.assertEqual(502, response.code)
        self.assertEqual(b"Facebook authorization failed", response.body)
        self.assertNotIn("provider-secret", "\n".join(logs.output))
        self.assertEqual([], self.graph.auth_calls)

    def test_oauth_callback_rejects_code_and_error_together(self):
        state, cookie_header = self._start_oauth()
        response = self.fetch(
            "/auth/login?code=code&error=access_denied&state=" + state,
            headers={"Cookie": cookie_header},
            follow_redirects=False,
        )

        self.assertEqual(400, response.code)
        self.assertEqual([], self.graph.auth_calls)


if __name__ == "__main__":
    unittest.main()
