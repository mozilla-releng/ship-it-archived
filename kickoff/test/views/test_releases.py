import simplejson as json

from kickoff import app
from kickoff.model import Release
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.client.get('/releases')
        expected = {
            'releases': ['foo11', 'bar12']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetIncompleteReleases(self):
        ret = self.client.get('/releases', query_string={'incomplete': True})
        expected = {
            'releases': ['foo11']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

class TestReleaseAPI(ViewTest):
    def testGetRelease(self):
        ret = self.client.get('/releases/bar12')
        expected = {
            'name': 'bar12',
            'submitter': 'joe',
            'product': 'bar',
            'version': '1',
            'buildNumber': 2,
            'mozillaRevision': 'abcd',
            'commRevision': None,
            'l10nChangesets': 'http://bar',
            'partials': '1,2',
            'whatsnew': True,
            'complete': True
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testMarkAsComplete(self):
        ret = self.client.post('/releases/foo11', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(Release.query.filter_by(name='foo11').first().complete, True)
