import tornado.web
import tornado.escape
import tornado.database
import tornado.auth

from tornado.options import define, options


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            return None
        return tornado.escape.json_decode(user_json)

    def write_error(self, status_code, **kwargs):
        print 'In get_error_html. status_code: ', status_code
        if status_code in [403, 404, 500, 503]:
            self.write('Sorry there was a problem')
        else:
            self.write('Sorry there was a problem')

    @property
    def db(self):
        return tornado.database.Connection(host=options.mysql_host,
                                           database=options.mysql_database, user=options.mysql_user,
                                           password=options.mysql_password)
