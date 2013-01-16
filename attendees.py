import tornado.web
import tornado.auth
import base
import json
from re import escape


class Attend(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        _event_id = self.get_argument('event_id')
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "INSERT INTO willbeout_attendees (user_id, event_id) VALUES (%s, %s)",
            _user_id, _event_id)
        self.redirect('/event?event_id=' + _event_id)

class AttendNo(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        _event_id = escape(self.get_argument('event_id'))
        _user_id = self.get_current_user()['id']
        a = self.db.execute(
            "DELETE FROM willbeout_attendees WHERE event_id = %s AND user_id  = %s",
            _event_id, _user_id,)
        _json = []
        for i in a:
            _json.append({'user_id': i['user_id']})
        self.write(json.dumps(_json))

class AttendData(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        _event_id = escape(self.get_argument('event_id'))
        a = self.db.query(
            "SELECT * FROM willbeout_attendees WHERE event_id = %s GROUP BY user_id",
            _event_id)
        _json = []
        for i in a:
            _json.append({'user_id': i['user_id']})
        self.write(json.dumps(_json))
