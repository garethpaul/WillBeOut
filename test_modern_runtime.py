import asyncio
import json
import unittest
from http.cookies import SimpleCookie
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlparse

from cryptography.fernet import Fernet
from tornado.httpclient import HTTPClientError
from tornado.testing import AsyncHTTPTestCase
from tornado.web import decode_signed_value

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
    def __init__(self):
        self.auth_calls = []

    def authorization_url(self, redirect_uri, state):
        return "https://www.facebook.com/v24.0/dialog/oauth?" + urlencode({
            "redirect_uri": redirect_uri,
            "state": state,
        })

    async def authenticate(self, redirect_uri, code):
        self.auth_calls.append((redirect_uri, code))
        return {"id": "42", "name": "Ada", "access_token": "secret-token"}

    async def request(self, _path, _access_token, **_parameters):
        return {"data": []}


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

        self.assertTrue(events.EventHandler._friendship_visible(None, payload, "42"))
        self.assertFalse(events.EventHandler._friendship_visible(None, payload, "99"))
        self.assertTrue(mobile.EventHandler._friendship_visible(None, payload, "42"))


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
