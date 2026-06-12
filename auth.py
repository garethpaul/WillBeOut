import hmac
import secrets

import tornado.web

import base
from facebook_client import FacebookClientError


class AuthLoginHandler(base.BaseHandler):
    def _redirect_uri(self):
        return self.settings["facebook_redirect_uri"]

    async def get(self):
        code = self.get_argument("code", None)
        if not code:
            state = secrets.token_urlsafe(32)
            self.set_secure_cookie(
                "facebook_oauth_state",
                state,
                httponly=True,
                secure=True,
                samesite="Lax",
                expires_days=10 / (24 * 60),
            )
            self.set_secure_cookie(
                "facebook_oauth_next",
                self.get_safe_next_url("/"),
                httponly=True,
                secure=True,
                samesite="Lax",
                expires_days=10 / (24 * 60),
            )
            self.redirect(self.facebook_client.authorization_url(self._redirect_uri(), state))
            return

        expected_state = self.get_secure_cookie("facebook_oauth_state")
        supplied_state = self.get_argument("state", "")
        try:
            valid_state = expected_state and hmac.compare_digest(
                expected_state.decode("ascii"), supplied_state
            )
        except UnicodeError:
            valid_state = False
        if not valid_state:
            raise tornado.web.HTTPError(400, "Invalid OAuth state")

        next_cookie = self.get_secure_cookie("facebook_oauth_next")
        next_url = next_cookie.decode("utf-8") if next_cookie else "/events"
        self.clear_cookie("facebook_oauth_state")
        self.clear_cookie("facebook_oauth_next")
        try:
            user = await self.facebook_client.authenticate(self._redirect_uri(), code)
        except FacebookClientError as error:
            raise tornado.web.HTTPError(502, "Facebook authentication failed") from error

        encrypted_user = self.application.settings["session_cipher"].encrypt_user(user)
        self.set_secure_cookie(
            "user",
            encrypted_user,
            httponly=True,
            secure=True,
            samesite="Lax",
            expires_days=1,
        )
        self.redirect(self.get_safe_next_url_value(next_url, "/events"))


class AuthLogoutHandler(base.BaseHandler):
    def post(self):
        self.clear_cookie("user")
        self.redirect("/")
