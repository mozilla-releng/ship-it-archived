from kickoff import app
from kickoff.model import FirefoxRelease
from kickoff.test.views.base import ViewTest

class TestSubmitRelease(ViewTest):
    def testSubmit(self):
        data = [
            'firefox-version=9.0',
            'firefox-buildNumber=1',
            'firefox-branch=z',
            'firefox-mozillaRevision=abc',
            'firefox-partials=1.0build1',
            'firefox-dashboardCheck=y',
            'firefox-l10nChangesets=af%20def',
            'firefox-product=firefox',
        ]
        ret = self.post('/submit_release.html', data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FirefoxRelease.query.filter_by(name='Firefox-9.0-build1').first()
            self.assertEquals(got.version, '9.0')
            self.assertEquals(got.buildNumber, 1)
            self.assertEquals(got.branch, 'z')
            self.assertEquals(got.mozillaRevision, 'abc')
            self.assertEquals(got.partials, '1.0build1')
            self.assertEquals(got.l10nChangesets, 'af def')
            self.assertEquals(got.ready, False)
            self.assertEquals(got.complete, False)
            self.assertEquals(got.status, '')

    def testSubmitInvalidForm(self):
        ret = self.post('/submit_release.html', data='fennec-product=fennec', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400, ret.data)
