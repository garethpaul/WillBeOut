import tornado.web
import base


class IndexHandler(base.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("mobile_index.html")

class EventsHandler(base.BaseHandler):
    @tornado.web.authenticated
    def get(self):
        _id = self.get_current_user()['id']
        events = self.db.query(
            "SELECT * FROM willbeout_events WHERE userid = %s AND DATE(f) >= DATE(NOW())", int(_id))
        self.render('mobile_events.html', events=events)



class EventHandler(base.BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        _eventid = self.get_int_argument('id')
        self.event = await self.require_event_access(_eventid)
        self.places = self.db.query("""select a.id, a.event_id, a.address, a.city, a.name, a.url, a.user_id, a.user_name, count(b.suggestion_id) as friends from willbeout_suggest as a
        LEFT JOIN willbeout_votes as b ON a.id = b.suggestion_id AND a.event_id = b.event_id
        WHERE a.event_id = %s
        GROUP BY a.id ORDER BY friends DESC;""", _eventid)
        self.render('mobile_event.html', event=self.event, places=self.places)
