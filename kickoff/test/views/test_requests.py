import simplejson as json

from kickoff import app
from kickoff.model import Release
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllRequests(self):
        ret = self.client.get('/requests')
        expected = {
            'foo11': {
                'name': 'foo11',
                'submitter': 'joe',
                'product': 'foo',
                'version': '1',
                'buildNumber': 1,
                'mozillaRevision': 'abc',
                'commRevision': None,
                'l10nChangesets': 'http://foo',
                'partials': '1,2',
                'whatsnew': False,
                'complete': False
            },
            'bar12': {
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
            },
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetIncompleteRequests(self):
        ret = self.client.get('/requests', query_string={'incomplete': True})
        expected = {
            'foo11': {
                'name': 'foo11',
                'submitter': 'joe',
                'product': 'foo',
                'version': '1',
                'buildNumber': 1,
                'mozillaRevision': 'abc',
                'commRevision': None,
                'l10nChangesets': 'http://foo',
                'partials': '1,2',
                'whatsnew': False,
                'complete': False
            },
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)


class TestReleaseAPI(ViewTest):
    def testMarkAsComplete(self):
        ret = self.client.post('/requests/foo11', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(Release.query.filter_by(name='foo11').first().complete, True)
