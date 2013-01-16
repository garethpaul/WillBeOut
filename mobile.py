import tornado.auth
import tornado.web
import base
import json
import urllib


class IndexHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
		self.render('mobile_index.html')

class EventsHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        _id = self.get_current_user()['id']
        events = self.db.query(
            "SELECT * FROM willbeout_events WHERE userid = %s AND DATE(f) >= DATE(NOW())", int(_id))
        self.render('mobile_events.html', events=events)



class EventHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        _id = self.get_argument('id')
        event = self.db.get(
            "SELECT * FROM willbeout_events WHERE id = %s", int(_id))
        places = self.db.query("""select a.id, a.event_id, a.address, a.city, a.name, a.url, a.user_id, a.user_name, count(b.suggestion_id) as friends from willbeout_suggest as a
        LEFT JOIN willbeout_votes as b ON a.id = b.suggestion_id
        WHERE a.event_id = %s
        GROUP BY a.id ORDER BY friends DESC;""", int(_id))
        self.render('mobile_event.html', event=event, places=places)