import tornado.web
import tornado.auth
import base
import json
from re import escape
import urllib


class DMHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        _id = self.get_argument('ide')
        _event_id = self.get_argument('event_id')
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "DELETE FROM willbeout_messages WHERE id = %s AND user_id = %s",
            _id, _user_id)
        self.redirect('/event?event_id=' + _event_id)


class MessageHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def get(self):
        event_id = self.get_argument('event_id')
        msgs = self.db.query(
            "SELECT id, user_id, msg, d FROM willbeout_messages WHERE event_id = %s ORDER BY d DESC",
            event_id)
        _json = []
        for i in msgs:
            _json.append({'id': i['id'], 'msg': urllib.unquote(i['msg']), 'user_id':
                         i['user_id'], 'd': i['d'].strftime("%A %d %b %Y")})
        self.write(json.dumps(_json))

    @tornado.web.authenticated
    def post(self):
        _id = self.get_current_user()['id']
        _msg = self.get_argument('msg')
        _event_id = self.get_argument('id')
        _name = self.get_current_user()['name']
        _type = self.get_argument('type', 'message')
        self.db.execute(
            "INSERT INTO willbeout_messages (user_id, msg, event_id, user_name) VALUES (%s, %s, %s, %s)",
            _id, urllib.quote(_msg), _event_id, _name)
        self.redirect('/event?event_id=' + _event_id)
