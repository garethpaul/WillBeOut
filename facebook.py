#!/usr/bin/env python
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.database
from base import *
import json
import urllib
from cgi import escape
from tornado.options import define, options
from prettydate import pdate
import time

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
       default="")
define("facebook_secret", help="your Facebook application secret",
       default="")
define('mysql_host', default='')
define('mysql_database', default='')
define('mysql_user', default='')
define('mysql_password', default='')


class Application(tornado.web.Application):
    def __init__(self):
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
            cookie_secret="12oETzKXQAGaYdkG5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
            ui_modules={"Post": PostModule},
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        # make it easy to connect to the database.
        self.db = tornado.database.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class FeedHandler(tornado.web.RequestHandler, tornado.auth.FacebookGraphMixin):
    def get(self):
        self.render('feedit.html')


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('index.html')

class Privacy(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render('privacy.html')

class SuggestHandler(BaseHandler, tornado.auth.FacebookGraphMixin):
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
