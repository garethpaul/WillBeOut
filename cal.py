import tornado.auth
import tornado.web
import base
import json
from cgi import escape


class CalHandler(base.BaseHandler):
    @tornado.web.authenticated
    def post(self):
        _user_id = self.get_current_user()['id']
        _user_name = self.get_current_user()['name']
        _hour = self.get_argument('hour')
        _day = self.get_argument('day')
        _date = self.get_argument('d')
        _month = self.get_argument('month')
        _week = self.get_argument('week')
        _string = self.get_argument('string')
        # check if vote exists
        c = self.db.execute(
            """INSERT INTO willbeout_times (user_id, user_name, hour, day, month, week, string, d) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            int(_user_id), escape(_user_name), str(_hour), str(_day), int(
            _month), int(_week), str(_string), int(_date))

        self.write('OK')

    @tornado.web.authenticated
    def get(self):
            _json = []
            _user_id = self.get_current_user()['id']
            _wk = self.get_argument('wk')

            for i in self.db.query(
                "SELECT * FROM willbeout_times WHERE user_id = %s AND week = %s",
                    escape(_user_id), _wk):
                _json.append({'day': str(i.day), 'month': i.month, 'hour':
                             i.hour, 'date': i.d, 'string': str(i.string)})

            self.write(json.dumps(_json))
