from datetime import datetime
import json
import mock
import os
from tempfile import mkstemp
import unittest

from kickoff import app, db
from kickoff.log import cef_config
from kickoff.model import FirefoxRelease, ThunderbirdRelease
from kickoff.views.forms import FirefoxReleaseForm, ThunderbirdReleaseForm


class TestFirefoxReleaseForm(unittest.TestCase):
    def setUp(self):
        self.cef_fd, self.cef_file = mkstemp()
        app.config['DEBUG'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config.update(cef_config(self.cef_file))
        with app.test_request_context():
            db.init_app(app)
            db.create_all()

            for i, version in enumerate(('48.0b7', '48.0b8', '48.0b9', '48.0', '48.0.1',
                                         '49.0b1', '49.0b2', '49.0b3')):
                branch = 'releases/mozilla-beta'
                if 'b' not in version:
                    branch = 'releases/mozilla-release'
                r = FirefoxRelease(partials='0,1', promptWaitTime=5,
                                   submitter='joe', version=version, buildNumber=1,
                                   branch=branch,
                                   mozillaRevision='def',
                                   l10nChangesets='ja zu',
                                   mozillaRelbranch='FOO',
                                   submittedAt=datetime(2015, 1, i+1, 3, 4, 5, 6),
                                   shippedAt=datetime(2015, 1, i+1, 7, 8, 9, 0),
                                   comment="yet an other amazing comment",
                                   description="we did this release because of foo")
                r.complete = True
                r.ready = True
                r.status = "shipped"
                db.session.add(r)

                r = ThunderbirdRelease(commRevision='zzz', commRelbranch=None,
                                       partials='0,1', promptWaitTime=5,
                                       submitter='joe', version=version, buildNumber=1,
                                       branch=branch, mozillaRevision='def',
                                       l10nChangesets='ja zu',
                                       mozillaRelbranch='FOO',
                                       submittedAt=datetime(2015, 1, i+1, 3, 4, 5, 6),
                                       shippedAt=datetime(2015, 1, i+1, 7, 8, 9, 0),
                                       comment="yet an other amazing comment",
                                       description="we did this release because of foo")
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

    def testFirefoxRCInsertion(self):
        with app.test_request_context():
            with mock.patch('kickoff.model.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2015, 2, 1)
                release = FirefoxReleaseForm()
                expected = json.dumps({
                    "releases/mozilla-beta": ["49.0b3build1", "49.0b2build1", "49.0b1build1", "48.0build1", "48.0b9build1", "48.0b8build1", "48.0b7build1"],
                    "releases/mozilla-release": ["48.0.1build1", "48.0build1"]
                })
                self.assertEqual(expected, release.partials.suggestions)

    def testThunberbird(self):
        with app.test_request_context():
            with mock.patch('kickoff.model.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime(2015, 2, 1)
                release = ThunderbirdReleaseForm()
                expected = json.dumps({
                    "releases/mozilla-beta": ["49.0b3build1", "49.0b2build1", "49.0b1build1", "48.0b9build1", "48.0b8build1", "48.0b7build1"],
                    "releases/mozilla-release": ["48.0.1build1", "48.0build1"]
                })
                self.assertEqual(expected, release.partials.suggestions)
