from datetime import datetime
import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.log import cef_config
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease


class TestBase(unittest.TestCase):
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
            r = FennecRelease(submitter='joe', version='1', buildNumber=1,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='af de', dashboardCheck=True,
                              mozillaRelbranch=None)
            r.ready = True
            db.session.add(r)
            r = FennecRelease(submitter='joe', version='4', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='gh ij', dashboardCheck=True,
                              mozillaRelbranch=None)
            db.session.add(r)
            r = FennecRelease(submitter='joe', version='4', buildNumber=5,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='lk mn', dashboardCheck=False,
                              mozillaRelbranch='BAR',
                              submittedAt=datetime(2005, 1, 2, 2, 3, 3, 5))
            db.session.add(r)
            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='2', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6))
            r.complete = True
            r.ready = True
            db.session.add(r)
            r = ThunderbirdRelease(commRevision='ghi', commRelbranch=None,
                                   partials='0', promptWaitTime=None,
                                   submitter='bob', version='2', buildNumber=2,
                                   branch='b', mozillaRevision='ghi',
                                   l10nChangesets='li', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1))
            r.complete = True
            r.ready = True
            db.session.add(r)
            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='4.0', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1))
            db.session.add(r)
            db.session.commit()

    def tearDown(self):
        # Trick Flask into thinking nothing has happened yet. Otherwise it will
        # complain when we try to reset the state in setUp().
        app._got_first_request = False
        os.close(self.db_fd)
        os.remove(self.db_file)
        os.close(self.cef_fd)
        os.remove(self.cef_file)
