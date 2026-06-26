import tornado.web
import base
import json
from re import escape
from urllib.parse import quote, unquote


class DMHandler(base.BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        _message_id = self.get_int_argument('ide')
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "DELETE FROM willbeout_messages WHERE id = %s AND user_id = %s AND event_id = %s",
            _message_id, _user_id, _event_id)
        self.redirect('/event?event_id=' + str(_event_id))


class MessageHandler(base.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("X-Content-Type-Options", "nosniff")
        msgs = self.db.query(
            "SELECT id, user_id, msg, d FROM willbeout_messages WHERE event_id = %s ORDER BY d DESC",
            _event_id)
        _json = []
        for i in msgs:
            _json.append({'id': i['id'], 'msg': unquote(i['msg']), 'user_id':
                         i['user_id'], 'd': i['d'].strftime("%A %d %b %Y")})
        self.write(json.dumps(_json))

    @tornado.web.authenticated
    async def post(self):
        _id = self.get_current_user()['id']
        _msg = self.get_argument('msg')
        _event_id = self.get_int_argument('id')
        await self.require_event_access(_event_id)
        _name = self.get_current_user()['name']
        _type = self.get_argument('type', 'message')
        self.db.execute(
            "INSERT INTO willbeout_messages (user_id, msg, event_id, user_name) VALUES (%s, %s, %s, %s)",
            _id, quote(_msg), _event_id, _name)
        self.redirect('/event?event_id=' + str(_event_id))
