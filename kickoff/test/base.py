from datetime import datetime
import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.log import cef_config
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease


class TestBase(unittest.TestCase):
    def setUp(self):
        self.cef_fd, self.cef_file = mkstemp()
        app.config['DEBUG'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config.update(cef_config(self.cef_file))
        with app.test_request_context():
            db.init_app(app)
            db.create_all()
            r = FennecRelease(submitter='joe', version='1', buildNumber=1,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"hi": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=True,
                              mozillaRelbranch=None)
            r.ready = True
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='4', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"fr": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=True,
                              mozillaRelbranch=None)
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='4', buildNumber=5,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"de": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=False,
                              mozillaRelbranch='BAR',
                              submittedAt=datetime(2005, 1, 2, 2, 3, 3, 5))
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='2.0', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 4, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               mh_changeset='xyz',
                               enUSPlatforms=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='2.0.2esr', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 4, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               enUSPlatforms=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='38.1.0esr', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2015, 1, 4, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               enUSPlatforms=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='24.0', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=True,
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 3, 1, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='24.0.1', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=True,
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='23.0b2', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              dashboardCheck=True,
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 2, 27, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b2', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               isSecurityDriven=True,
                               description="We did this because of an issue in NSS",
                               enUSPlatforms=None)
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b2', buildNumber=2,
                               branch='a', mozillaRevision='defa',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 3, 2, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               enUSPlatforms=None)
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0.1', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu', dashboardCheck=True,
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazying comment",
                               enUSPlatforms=None,
                               description="we did this release because of foo")
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)

            # Thunderbird data
            r = ThunderbirdRelease(commRevision='ghi', commRelbranch=None,
                                   partials='0', promptWaitTime=None,
                                   submitter='bob', version='2', buildNumber=2,
                                   branch='b', mozillaRevision='ghi',
                                   l10nChangesets='li', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 1, 3, 1, 1, 1, 1),
                                   comment='My great comment!',
                                   enUSPlatforms="foo bar",
                                   isSecurityDriven=True,
                                   mh_changeset='xyz',
                                   description="we did this release because of bar")
            r.complete = True
            r.ready = True
            db.session.add(r)

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='4.0', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   description="foo reason")
            db.session.add(r)
            db.session.commit()

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='23.0', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 1, 3, 1, 1, 1, 1),
                                   description="bar reason")
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)
            db.session.commit()

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='23.0.1', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2014, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2014, 2, 3, 1, 1, 1, 1),
                                   description="bar2 reason")
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)
            db.session.commit()

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='24.0b2', buildNumber=2,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz', dashboardCheck=True,
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 2, 1, 1, 1, 1, 1),
                                   description="bar2 reason")
            r.complete = True
            r.ready = True
            # Shipped
            r.status = "postrelease"
            db.session.add(r)
            db.session.commit()

    def tearDown(self):
        # Trick Flask into thinking nothing has happened yet. Otherwise it will
        # complain when we try to reset the state in setUp().
        app._got_first_request = False
        os.close(self.cef_fd)
        os.remove(self.cef_file)
