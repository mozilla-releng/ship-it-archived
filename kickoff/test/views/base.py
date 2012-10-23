import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.model import Release

class ViewTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_file = mkstemp()
        app.config['DEBUG'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_file
        with app.test_request_context():
            db.init_app(app)
            db.create_all()
            db.session.add(Release('joe', 'foo', '1', 1, 'abc', 'http://foo', '1,2', False))
            r = Release('joe', 'bar', '1', 2, 'abcd', 'http://bar', '1,2', True)
            r.complete = True
            db.session.add(r)
            db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        # Trick Flask into thinking nothing has happened yet. Otherwise it will
        # complain when we try to reset the state in setUp().
        app._got_first_request = False
        os.close(self.db_fd)
        os.remove(self.db_file)
