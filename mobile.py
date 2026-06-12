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
        self.access = 0
        _eventid = self.get_int_argument('id')
        _id = self.get_current_user()['id']
        self.event = self.db.get(
            "SELECT * FROM willbeout_events WHERE id = %s", _eventid)
        if not self.event:
            raise tornado.web.HTTPError(404)
        self.places = self.db.query("""select a.id, a.event_id, a.address, a.city, a.name, a.url, a.user_id, a.user_name, count(b.suggestion_id) as friends from willbeout_suggest as a
        LEFT JOIN willbeout_votes as b ON a.id = b.suggestion_id
        WHERE a.event_id = %s
        GROUP BY a.id ORDER BY friends DESC;""", _eventid)
        owner_id = str(self.event['userid'])
        if owner_id == _id:
            self.access = 1
        streams = await self.facebook_request(
            "/me/friends", self.current_user["access_token"], fields="id", limit=500
        )
        self._go(streams, owner_id)

    def _friendship_visible(self, streams, owner_id):
        if isinstance(streams, dict):
            data = streams.get("data")
            return isinstance(data, list) and any(
                isinstance(friend, dict) and str(friend.get("id")) == owner_id
                for friend in data
            )
        return False

    def _go(self, streams, owner_id):
        if self.access != 1 and not self._friendship_visible(streams, owner_id):
            raise tornado.web.HTTPError(403)

        self.render('mobile_event.html', event=self.event, places=self.places)
