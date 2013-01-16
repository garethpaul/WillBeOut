import tornado.auth
import tornado.web
import base
import json
import urllib


class EventHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        # access trigger
        self.access = 0
        _eventid = self.get_argument('event_id')
        _id = self.get_current_user()['id']
        # get owner_id
        print 'checkpoint 1'
        self.event = self.db.get(
            "SELECT * FROM willbeout_events WHERE id = %s", int(_eventid))
        self.suggest = self.db.query("""select a.id, a.event_id, a.address, a.city, a.name, a.url, a.user_id, a.user_name, count(b.suggestion_id) as friends from willbeout_suggest as a
        LEFT JOIN willbeout_votes as b ON a.id = b.suggestion_id
        WHERE a.event_id = %s
        GROUP BY a.id ORDER BY friends DESC;""", int(_eventid))
        self.votes = self.db.query("""select suggestion_id from willbeout_votes where event_id = %s and user_id = %s group by suggestion_id;
        """, int(_eventid), int(_id))

        if str(self.event['userid']).strip('L') == _id:
            self.access = 1
        self.facebook_request("/me/friends/" + str(self.event['userid']), self
            ._go, access_token=self.current_user["access_token"])

    def _go(self, streams):
        try:
            self.render('event.html', event=self.event, suggestions=self.
                        suggest, votes=self.votes, x=self.xsrf_form_html())
        except:
            self.redirect('/problem')
            pass

class EventsHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        x = self.xsrf_form_html()
        _id = self.get_current_user()['id']
        events = self.db.query(
            "SELECT * FROM willbeout_events WHERE userid = %s AND DATE(f) >= DATE(NOW()) ORDER BY f DESC", int(_id))
        self.render("events.html", x=x, events=events)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self):
        _id = self.get_current_user()['id']
        _place = self.get_argument('place')
        _from = self.get_argument('from')
        _to = self.get_argument('to')
        self.db.execute(
            "INSERT INTO willbeout_events (userid, place, f, t) VALUES (%s, %s, %s, %s)",
            int(_id), _place, _from, _to)
        self.redirect('/events')


class TimeHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def post(self):
        _user_id = self.get_current_user()['id']
        _user_name = self.get_current_user()['name']
        _event_id = self.get_argument('event_id')
        _times = self.get_argument('availabletimes')
        self.db.execute(
            "DELETE FROM willbeout_availability WHERE event_id = %s and user_id = %s",
            int(_event_id), int(_user_id))

        for i in urllib.unquote(_times).split(','):
            self.db.execute(
                """INSERT INTO willbeout_availability (user_id, user_name, time, event_id) VALUES (%s, %s, %s, %s)""",
                int(_user_id), _user_name, int(i), _event_id)
        self.redirect('/event?event_id=' + _event_id)

    @tornado.web.authenticated
    def get(self):
        _json = []
        _event_id = self.get_argument('event_id')
        for i in self.db.query(
            'SELECT * FROM willbeout_availability WHERE event_id = %s ORDER BY time',
                int(_event_id)):
            _json.append({'time': int(i['time']), 'user': int(
                i['user_id']), 'name': str(i['user_name'])})
        self.write(json.dumps(_json))
