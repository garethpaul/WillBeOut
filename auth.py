import base
import tornado.auth
import tornado.escape
import tornado.web
import auth
import re
from ismobile import check

class AuthLoginHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        my_url = (self.request.protocol + "://" + self.request.host +
                  "/auth/login?next=" +
                  tornado.escape.url_escape(self.get_argument("next", "/")))
        if self.get_argument("code", False):
            self.get_authenticated_user(redirect_uri=my_url, client_id=self.
                                        settings["facebook_api_key"], client_secret=self.settings[
                                        "facebook_secret"], code=self.get_argument("code"),
                                        callback=self._on_auth)
            return
        self.authorize_redirect(redirect_uri=my_url, client_id=self.settings[
            "facebook_api_key"], extra_params={"scope": "read_friendlists"})

    def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, "Facebook auth failed")
        self.set_secure_cookie("user", tornado.escape.json_encode(user))
        #magic redirect to mobile if mobile or desktop if desktop
        user_agent = self.request.headers.get("User-Agent")
        if check(user_agent) == 1:
            self.redirect(self.get_argument("next", "../events"))
        else:
            self.redirect(self.get_argument("next", "../events"))åå

class AuthLogoutHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    def get(self):
        self.clear_cookie("user")
        self.redirect('https://www.facebook.com/logout.php')
