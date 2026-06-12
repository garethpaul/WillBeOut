import tornado.web
import tornado.escape


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        encrypted_user = self.get_secure_cookie("user")
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
