import tornado.web
import base
import json


class Attend(base.BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "INSERT INTO willbeout_attendees (user_id, event_id) VALUES (%s, %s)",
            _user_id, _event_id)
        self.redirect('/event?event_id=' + str(_event_id))

class AttendNo(base.BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "DELETE FROM willbeout_attendees WHERE event_id = %s AND user_id  = %s",
            _event_id, _user_id,)
        self.redirect('/event?event_id=' + str(_event_id))

class AttendData(base.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        a = self.db.query(
            "SELECT * FROM willbeout_attendees WHERE event_id = %s GROUP BY user_id",
            _event_id)
        _json = []
        for i in a:
            _json.append({'user_id': i['user_id']})
        self.write(json.dumps(_json))
