import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.log import cef_config
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease

class ViewTest(unittest.TestCase):
    auth = {'REMOTE_USER': 'bob'}

    def setUp(self):
        self.db_fd, self.db_file = mkstemp()
        self.cef_fd, self.cef_file = mkstemp()
        app.config['DEBUG'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_file
        app.config.update(cef_config(self.cef_file))
        with app.test_request_context():
            db.init_app(app)
            db.create_all()
            r = FennecRelease('joe', '1', 1, 'a', 'abc', 'af de', True)
            r.ready = True
            db.session.add(r)
            r = FennecRelease('joe', '4', 4, 'a', 'abc', 'gh ij', True)
            db.session.add(r)
            r = FennecRelease('joe', '4', 5, 'a', 'abc', 'kl mn', False)
            db.session.add(r)
            r = FirefoxRelease('0,1', 'joe', '2', 1, 'a', 'def', 'ja zu', True)
            r.complete = True
            r.ready = True
            db.session.add(r)
            r = ThunderbirdRelease('ghi', '0', 'bob', '2', 2, 'b', 'ghi', 'li', True)
            r.complete = True
            r.ready = True
            db.session.add(r)
            db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        # Trick Flask into thinking nothing has happened yet. Otherwise it will
        # complain when we try to reset the state in setUp().
        app._got_first_request = False
        os.close(self.db_fd)
        os.remove(self.db_file)
        os.close(self.cef_fd)
        os.remove(self.cef_file)

    def get(self, *args, **kwargs):
        return self.client.get(*args, environ_base=self.auth, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, environ_base=self.auth, **kwargs)
