import simplejson as json

from kickoff import app
from kickoff.model import Release
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.client.get('/releases')
        expected = {
            'releases': ['foo-1-1', 'bar-1-2']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetIncompleteReleases(self):
        ret = self.client.get('/releases', query_string={'incomplete': True})
        expected = {
            'releases': ['foo-1-1']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

class TestReleaseAPI(ViewTest):
    def testGetRelease(self):
        ret = self.client.get('/releases/bar-1-2')
        expected = {
            'name': 'bar-1-2',
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
        ret = self.client.post('/releases/foo-1-1', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(Release.query.filter_by(name='foo-1-1').first().complete, True)
