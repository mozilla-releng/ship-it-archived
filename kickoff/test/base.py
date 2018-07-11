from datetime import datetime
import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.log import cef_config
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease, \
    DeveditionRelease


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
            r = FennecRelease(submitter='joe', version='1.0', buildNumber=1,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"hi": { "revision": "fe436c75f71d" }}',
                              mozillaRelbranch=None)
            r.ready = True
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='4.0', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"fr": { "revision": "fe436c75f71d" }}',
                              mozillaRelbranch=None)
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='4.0', buildNumber=5,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"de": { "revision": "fe436c75f71d", "platforms": ["android", "android-multilocale"]  }}',
                              mozillaRelbranch='BAR',
                              submittedAt=datetime(2005, 1, 2, 2, 3, 3, 5))
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='2.0', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 4, 3, 4, 5, 6),
                               comment="yet an other amazing comment",
                               mh_changeset='xyz')
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            three_digit_esr_release = FirefoxRelease(
                partials='0,1', promptWaitTime=5,
                submitter='joe', version='2.0.2esr', buildNumber=1,
                branch='a', mozillaRevision='def',
                l10nChangesets='ja zu',
                mozillaRelbranch='FOO',
                submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                shippedAt=datetime(2005, 1, 4, 3, 4, 5, 6),
                comment="yet an other amazing comment"
            )
            three_digit_esr_release.complete = True
            three_digit_esr_release.ready = True
            three_digit_esr_release.status = "shipped"
            db.session.add(three_digit_esr_release)

            two_digit_esr_release = FirefoxRelease(
                partials='0,1', promptWaitTime=5,
                submitter='joe', version='38.0esr', buildNumber=1,
                branch='a', mozillaRevision='def',
                l10nChangesets='ja zu',
                mozillaRelbranch='FOO',
                submittedAt=datetime(2015, 1, 2, 3, 4, 5, 6),
                shippedAt=datetime(2015, 1, 4, 3, 4, 5, 6),
                comment="yet an other amazing comment"
            )
            two_digit_esr_release.complete = True
            two_digit_esr_release.ready = True
            two_digit_esr_release.status = "shipped"
            db.session.add(two_digit_esr_release)

            r = FennecRelease(submitter='joe', version='24.0', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d" }}',
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 3, 1, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='24.0.1', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d" }}',
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FennecRelease(submitter='joe', version='23.0b2', buildNumber=4,
                              branch='a', mozillaRevision='abc',
                              l10nChangesets='{"an": { "revision": "fe436c75f71d" }}',
                              submittedAt=datetime(2015, 2, 26, 3, 4, 5, 6),
                              shippedAt=datetime(2015, 2, 27, 3, 4, 5, 6),
                              mozillaRelbranch=None)
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='1.0.9', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='legacy',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazing comment",
                               description="we did this release because of foo")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b1', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="Rule with release_eta",
                               description="Rule with release_eta",
                               release_eta=datetime(2005, 1, 2, 3, 4, 5, 7))
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)


            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b2', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazing comment",
                               isSecurityDriven=True,
                               description="We did this because of an issue in NSS")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b2', buildNumber=2,
                               branch='a', mozillaRevision='defa',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazing comment",
                               release_eta=datetime(2005, 1, 2, 3, 4, 5, 7))
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0b3', buildNumber=1,
                               branch='a', mozillaRevision='defau',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 2, 3, 4, 5, 6, 7),
                               shippedAt=datetime(2005, 2, 3, 4, 5, 6, 7),
                               comment="yet an other amazing comment",
                               isSecurityDriven=True,
                               description="Another beta release for Firefox 3")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                               submitter='joe', version='3.0.1', buildNumber=1,
                               branch='a', mozillaRevision='def',
                               l10nChangesets='ja zu',
                               mozillaRelbranch='FOO',
                               submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                               comment="yet an other amazing comment",
                               description="we did this release because of foo")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = DeveditionRelease(
                partials='0,1', promptWaitTime=5, submitter='joe',
                version='3.0b5', buildNumber=1, branch='a',
                mozillaRevision='def', l10nChangesets='ja zu',
                mozillaRelbranch='FOO',
                submittedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                shippedAt=datetime(2005, 1, 2, 3, 4, 5, 6),
                comment="yet an other amazing comment",
                description="we did this release because of foo")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            # Thunderbird data
            r = ThunderbirdRelease(commRevision='ghi', commRelbranch=None,
                                   partials='0', promptWaitTime=None,
                                   submitter='bob', version='2.0', buildNumber=2,
                                   branch='b', mozillaRevision='ghi',
                                   l10nChangesets='li',
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 1, 3, 1, 1, 1, 1),
                                   comment='My great comment!',
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
                                   l10nChangesets='yy zz',
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   description="foo reason")
            db.session.add(r)

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='23.0', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz',
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 1, 3, 1, 1, 1, 1),
                                   description="bar reason")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='23.0.1', buildNumber=1,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz',
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2014, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2014, 2, 3, 1, 1, 1, 1),
                                   description="bar2 reason")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                   partials='1.0build1', promptWaitTime=None,
                                   submitter='bob', version='24.0b2', buildNumber=2,
                                   branch='b', mozillaRevision='yyy',
                                   l10nChangesets='yy zz',
                                   mozillaRelbranch=None,
                                   submittedAt=datetime(2005, 1, 1, 1, 1, 1, 1),
                                   shippedAt=datetime(2005, 2, 1, 1, 1, 1, 1),
                                   description="bar2 reason")
            r.complete = True
            r.ready = True
            r.status = "shipped"
            db.session.add(r)

            db.session.commit()

    def tearDown(self):
        # Trick Flask into thinking nothing has happened yet. Otherwise it will
        # complain when we try to reset the state in setUp().
        app._got_first_request = False
        os.close(self.cef_fd)
        os.remove(self.cef_file)
