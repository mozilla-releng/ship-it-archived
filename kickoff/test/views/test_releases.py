import simplejson as json

from kickoff import app
from kickoff.model import FirefoxRelease
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.get('/releases')
        expected = {
            'releases': ['Fennec-1-build1', 'Firefox-2-build1', 'Thunderbird-2-build2']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetIncompleteReleases(self):
        ret = self.get('/releases', query_string={'incomplete': True})
        expected = {
            'releases': ['Fennec-1-build1']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

class TestReleaseAPI(ViewTest):
    def testGetRelease(self):
        ret = self.get('/releases/Thunderbird-2-build2')
        expected = {
            'name': 'Thunderbird-2-build2',
            'product': 'thunderbird',
            'submitter': 'bob',
            'version': '2',
            'buildNumber': 2,
            'branch': 'b',
            'mozillaRevision': 'ghi',
            'commRevision': 'ghi',
            'l10nChangesets': 'http://baz',
            'partials': '0',
            'complete': True
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testMarkAsComplete(self):
        ret = self.post('/releases/Firefox-2-build1', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FirefoxRelease.query.filter_by(name='Firefox-2-build1').first().complete, True)
