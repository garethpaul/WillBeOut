import tornado.web
import base
import json
from urllib.parse import unquote


class EventHandler(base.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        _eventid = self.get_int_argument('event_id')
        self.event = await self.require_event_access(_eventid)
        self.suggest = self.db.query("""select a.id, a.event_id, a.address, a.city, a.name, a.url, a.user_id, a.user_name, count(b.suggestion_id) as friends from willbeout_suggest as a
        LEFT JOIN willbeout_votes as b ON a.id = b.suggestion_id
        WHERE a.event_id = %s
        GROUP BY a.id ORDER BY friends DESC;""", _eventid)
        self.votes = self.db.query("""select suggestion_id from willbeout_votes where event_id = %s and user_id = %s group by suggestion_id;
        """, _eventid, int(_id))

        self.render(
            "event.html",
            event=self.event,
            suggestions=self.suggest,
            votes=self.votes,
            x=self.xsrf_form_html(),
        )

class EventsHandler(base.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        x = self.xsrf_form_html()
        _id = self.get_current_user()['id']
        events = self.db.query(
            "SELECT * FROM willbeout_events WHERE userid = %s AND DATE(f) >= DATE(NOW()) ORDER BY f DESC", int(_id))
        self.render("events.html", x=x, events=events)

    @tornado.web.authenticated
    def post(self):
        _id = self.get_current_user()['id']
        _place = self.get_argument('place')
        _from = self.get_argument('from')
        _to = self.get_argument('to')
        self.db.execute(
            "INSERT INTO willbeout_events (userid, place, f, t) VALUES (%s, %s, %s, %s)",
            int(_id), _place, _from, _to)
        self.redirect('/events')


class TimeHandler(base.BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        _user_id = self.get_current_user()['id']
        _user_name = self.get_current_user()['name']
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        _times = self.get_argument('availabletimes')
        self.db.execute(
            "DELETE FROM willbeout_availability WHERE event_id = %s and user_id = %s",
            _event_id, int(_user_id))

        for i in unquote(_times).split(','):
            self.db.execute(
                """INSERT INTO willbeout_availability (user_id, user_name, time, event_id) VALUES (%s, %s, %s, %s)""",
                int(_user_id), _user_name, int(i), _event_id)
        self.redirect('/event?event_id=' + str(_event_id))

    @tornado.web.authenticated
    async def get(self):
        _json = []
        _event_id = self.get_int_argument('event_id')
        await self.require_event_access(_event_id)
        for i in self.db.query(
            'SELECT * FROM willbeout_availability WHERE event_id = %s ORDER BY time',
                _event_id):
            _json.append({'time': int(i['time']), 'user': int(
                i['user_id']), 'name': str(i['user_name'])})
        self.write(json.dumps(_json))
