import simplejson as json

from kickoff import app
from kickoff.model import FennecRelease, FirefoxRelease
from kickoff.test.views.base import ViewTest

class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.get('/releases')
        expected = {
            'releases': ['Fennec-1-build1', 'Fennec-4-build4', 'Fennec-4-build5', 'Firefox-2-build1', 'Thunderbird-2-build2']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetReadyReleases(self):
        ret = self.get('/releases', query_string={'ready': 1, 'complete': 0})
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
            'ready': True,
            'complete': True,
            'status': ''
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testMarkAsComplete(self):
        ret = self.post('/releases/Firefox-2-build1', data={'complete': True})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FirefoxRelease.query.filter_by(name='Firefox-2-build1').first().complete, True)

    def testUpdateStatus(self):
        ret = self.post('/releases/Fennec-1-build1', data={'status': 'omg!'})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-1-build1').first().status, 'omg!')


class TestReleasesView(ViewTest):
    def testMakeReady(self):
        ret = self.post('/releases.html', data='readyReleases=Fennec-4-build4&readyReleases=Fennec-4-build5', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build4').first().ready, True)
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build5').first().ready, True)
