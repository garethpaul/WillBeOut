import tornado.web
import tornado.escape


class BaseHandler(tornado.web.RequestHandler):
    USER_COOKIE_MAX_AGE_DAYS = 1
    OAUTH_COOKIE_MAX_AGE_DAYS = 10 / (24 * 60)

    def get_current_user(self):
        encrypted_user = self.get_secure_cookie(
            "user", max_age_days=self.USER_COOKIE_MAX_AGE_DAYS
        )
        if not encrypted_user:
            return None
        try:
            encrypted_user = encrypted_user.decode("ascii")
        except UnicodeError:
            return None
        return self.application.settings["session_cipher"].decrypt_user(encrypted_user)

    def get_safe_next_url(self, default="/events"):
        return self.get_safe_next_url_value(self.get_argument("next", default), default)

    @staticmethod
    def get_safe_next_url_value(next_url, default="/events"):
        if next_url == "/":
            return "/"
        if next_url == "/events":
            return "/events"
        if default == "/":
            return "/"
        return "/events"

    def get_int_argument(self, name):
        value = self.get_argument(name)
        try:
            return int(value)
        except (TypeError, ValueError):
            raise tornado.web.HTTPError(400)

    def write_error(self, status_code, **kwargs):
        self.write("Sorry there was a problem")

    @property
    def db(self):
        return self.application.settings["database"]

    @property
    def facebook_client(self):
        return self.application.settings["facebook_client"]

    async def facebook_request(self, path, access_token, **parameters):
        return await self.facebook_client.request(path, access_token, **parameters)

    @staticmethod
    def friendship_visible(streams, owner_id):
        if not isinstance(streams, dict):
            return False
        data = streams.get("data")
        return isinstance(data, list) and any(
            isinstance(friend, dict) and str(friend.get("id")) == str(owner_id)
            for friend in data
        )

    async def require_event_access(self, event_id):
        event = self.db.get(
            "SELECT * FROM willbeout_events WHERE id = %s", event_id
        )
        if not event:
            raise tornado.web.HTTPError(404)

        current_user = self.get_current_user()
        owner_id = str(event["userid"])
        if owner_id == str(current_user["id"]):
            return event

        streams = await self.facebook_request(
            "/me/friends", current_user["access_token"], fields="id", limit=500
        )
        if not self.friendship_visible(streams, owner_id):
            raise tornado.web.HTTPError(403)
        return event

    def require_event_suggestion(self, suggestion_id, event_id):
        suggestion = self.db.get(
            "SELECT id FROM willbeout_suggest WHERE id = %s AND event_id = %s",
            suggestion_id,
            event_id,
        )
        if not suggestion:
            raise tornado.web.HTTPError(404)
        return suggestion
