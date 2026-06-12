#!/usr/bin/env python
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from base import BaseHandler
from html import escape
from tornado.options import define, options
from database import Database
from facebook_client import FacebookClient
from session import SessionCipher

#modules
import auth
import events
import cal
import messages
import votes
import mobile
import attendees


define("port", default=os.environ.get(
    "PORT", 5000), help="run on the given port", type=int)
define("facebook_api_key", help="your Facebook API key",
       default=os.environ.get("FACEBOOK_API_KEY", ""))
define("facebook_secret", help="your Facebook application secret",
       default=os.environ.get("FACEBOOK_SECRET", ""))
define("facebook_graph_version", default=os.environ.get("FACEBOOK_GRAPH_VERSION", "v24.0"))
define("facebook_redirect_uri", default=os.environ.get("FACEBOOK_REDIRECT_URI", ""))
define("cookie_secret", help="Tornado secure-cookie signing secret",
       default=os.environ.get("COOKIE_SECRET", ""))
define("session_encryption_key", default=os.environ.get("SESSION_ENCRYPTION_KEY", ""))
define("mysql_host", default=os.environ.get("MYSQL_HOST", ""))
define("mysql_database", default=os.environ.get("MYSQL_DATABASE", ""))
define("mysql_user", default=os.environ.get("MYSQL_USER", ""))
define("mysql_password", default=os.environ.get("MYSQL_PASSWORD", ""))


class Application(tornado.web.Application):
    def __init__(
        self,
        database=None,
        facebook_client=None,
        session_cipher=None,
        cookie_secret=None,
        facebook_redirect_uri=None,
    ):
        configured_cookie_secret = cookie_secret or options.cookie_secret
        if not configured_cookie_secret:
            raise RuntimeError("COOKIE_SECRET is required")
        configured_redirect_uri = facebook_redirect_uri or options.facebook_redirect_uri
        if not configured_redirect_uri.startswith("https://"):
            raise RuntimeError("FACEBOOK_REDIRECT_URI must use HTTPS")
        handlers = [
			(r"/", MainHandler),
			(r"/calendar/post", cal.CalHandler),
			(r"/calendar/get", cal.CalHandler),
			(r"/event", events.EventHandler),
			(r"/time", events.TimeHandler),
			(r"/vote", votes.VoteHandler),
			(r"/change/vote", votes.ChangeVoteHandler),
			(r"/suggest", SuggestHandler),
			(r"/feed", FeedHandler),
			(r"/attend", attendees.Attend),
			(r"/attend/no", attendees.AttendNo),
			(r"/attend/data", attendees.AttendData),
			(r"/events", events.EventsHandler),
			(r"/messages", messages.MessageHandler),
			(r"/delete/message", messages.DMHandler),
			(r"/auth/login", auth.AuthLoginHandler),
			(r"/auth/logout", auth.AuthLogoutHandler),
			# mobile
			(r"/mobile", mobile.IndexHandler),
			(r"/mobile/events", mobile.EventsHandler),
			(r"/mobile/event", mobile.EventHandler),
			# legal
			(r"/privacy", Privacy),
        ]
        settings = dict(
            cookie_secret=configured_cookie_secret,
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
            ui_modules={"Post": PostModule},
            autoescape="xhtml_escape",
            database=database or Database(
                host=options.mysql_host,
                database=options.mysql_database,
                user=options.mysql_user,
                password=options.mysql_password,
            ),
            facebook_client=facebook_client or FacebookClient(
                options.facebook_api_key,
                options.facebook_secret,
                version=options.facebook_graph_version,
            ),
            session_cipher=session_cipher or SessionCipher(options.session_encryption_key),
            facebook_redirect_uri=configured_redirect_uri,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class FeedHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('feedit.html')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class Privacy(tornado.web.RequestHandler):
	def get(self):
		self.render('privacy.html')

class SuggestHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        _user_id = self.get_current_user()['id']
        _user_name = self.get_current_user()['name']
        _name = escape(self.get_argument('name'))
        _url = escape(self.get_argument('url'))
        _address = escape(self.get_argument('address'))
        _city = escape(self.get_argument('city'))
        _event_id = escape(self.get_argument('event_id'))
        self.db.execute("""INSERT INTO willbeout_suggest (user_id,
                                                    user_name,
                                                    event_id,
                                                    name,
                                                    city,
                                                    address,
                                                    url) VALUES (
                                                        %s, %s, %s, %s, %s, %s, %s)""",
                        int(_user_id), _user_name, int(
                            _event_id), _name, _city, _address,
                        _url)

        self.write('OK')


class PostModule(tornado.web.UIModule):
    def render(self, post):
        return self.render_string("modules/post.html", post=post)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
