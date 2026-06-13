import hmac
import secrets

import tornado.web

import base
from facebook_client import FacebookClientError


class AuthLoginHandler(base.BaseHandler):
    def _redirect_uri(self):
        return self.settings["facebook_redirect_uri"]

    def _finish_oauth_error(self, status, message):
        self.set_status(status)
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.finish(message)

    async def get(self):
        has_code = "code" in self.request.arguments
        has_error = "error" in self.request.arguments
        if not (has_code or has_error):
            state = secrets.token_urlsafe(32)
            self.set_secure_cookie(
                "facebook_oauth_state",
                state,
                httponly=True,
                secure=True,
                samesite="Lax",
                expires_days=self.OAUTH_COOKIE_MAX_AGE_DAYS,
            )
            self.set_secure_cookie(
                "facebook_oauth_next",
                self.get_safe_next_url("/"),
                httponly=True,
                secure=True,
                samesite="Lax",
                expires_days=self.OAUTH_COOKIE_MAX_AGE_DAYS,
            )
            self.redirect(self.facebook_client.authorization_url(self._redirect_uri(), state))
            return

        code = self.get_argument("code", "")
        expected_state = self.get_secure_cookie(
            "facebook_oauth_state", max_age_days=self.OAUTH_COOKIE_MAX_AGE_DAYS
        )
        supplied_state = self.get_argument("state", "")
        try:
            valid_state = expected_state and hmac.compare_digest(
                expected_state.decode("ascii"), supplied_state
            )
        except UnicodeError:
            valid_state = False
        if not valid_state:
            self._finish_oauth_error(400, "Invalid OAuth state")
            return

        next_cookie = self.get_secure_cookie(
            "facebook_oauth_next", max_age_days=self.OAUTH_COOKIE_MAX_AGE_DAYS
        )
        next_url = next_cookie.decode("utf-8") if next_cookie else "/events"
        self.clear_cookie("facebook_oauth_state")
        self.clear_cookie("facebook_oauth_next")
        if has_code and has_error:
            self._finish_oauth_error(400, "Ambiguous OAuth callback")
            return
        if has_error:
            if self.get_argument("error", "") == "access_denied":
                self._finish_oauth_error(403, "Facebook authorization denied")
                return
            self._finish_oauth_error(502, "Facebook authorization failed")
            return
        if not code:
            self._finish_oauth_error(400, "Missing OAuth code")
            return
        try:
            user = await self.facebook_client.authenticate(self._redirect_uri(), code)
        except FacebookClientError as error:
            self._finish_oauth_error(502, "Facebook authentication failed")
            return

        encrypted_user = self.application.settings["session_cipher"].encrypt_user(user)
        self.set_secure_cookie(
            "user",
            encrypted_user,
            httponly=True,
            secure=True,
            samesite="Lax",
            expires_days=self.USER_COOKIE_MAX_AGE_DAYS,
        )
        self.redirect(self.get_safe_next_url_value(next_url, "/events"))


class AuthLogoutHandler(base.BaseHandler):
    def post(self):
        self.clear_cookie("user")
        self.redirect("/")
