import simplejson as json

from kickoff import app
from kickoff.model import FirefoxRelease
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.get('/releases')
        expected = {
            'releases': ['fennec-1-1', 'firefox-2-1', 'thunderbird-2-2']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetIncompleteReleases(self):
        ret = self.get('/releases', query_string={'incomplete': True})
        expected = {
            'releases': ['fennec-1-1']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

class TestReleaseAPI(ViewTest):
    def testGetRelease(self):
        ret = self.get('/releases/thunderbird-2-2')
        expected = {
            'name': 'thunderbird-2-2',
            'submitter': 'bob',
            'version': '2',
            'buildNumber': 2,
            'mozillaRevision': 'ghi',
            'commRevision': 'ghi',
            'l10nChangesets': 'http://baz',
            'partials': '0',
            'whatsnew': True,
            'complete': True
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testMarkAsComplete(self):
        ret = self.post('/releases/firefox-2-1', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FirefoxRelease.query.filter_by(name='firefox-2-1').first().complete, True)
