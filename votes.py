import base
import tornado.auth
import tornado.web

class VoteHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def post(self):
        _user_id = self.get_current_user()['id']
        _user_name = self.get_current_user()['name']
        _event_id = self.get_int_argument('event_id')
        _suggestion_id = self.get_int_argument('id')
        # check if vote exists
        c = self.db.execute_rowcount(
            "SELECT * FROM willbeout_votes WHERE user_id = %s and event_id = %s and suggestion_id = %s",
            int(_user_id), _event_id, _suggestion_id)
        if c == 0:
            self.db.execute_rowcount("""INSERT INTO willbeout_votes (user_id,
                                                                event_id,
                                                                suggestion_id,
                                                                user_name) VALUES (%s, %s, %s, %s)""",
                                     int(_user_id), _event_id, _suggestion_id, _user_name
                                     )

            self.redirect('/event?event_id=' + str(_event_id))
        else:
            self.redirect('/event?event_id=' + str(_event_id))

class ChangeVoteHandler(base.BaseHandler, tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    def post(self):
        _suggestion_id = self.get_int_argument('id')
        _event_id = self.get_int_argument('event_id')
        _user_id = self.get_current_user()['id']
        self.db.execute(
            "DELETE FROM willbeout_votes WHERE suggestion_id = %s AND user_id = %s AND event_id = %s",
            _suggestion_id, int(_user_id), _event_id)

        self.redirect('/event?event_id=' + str(_event_id))
