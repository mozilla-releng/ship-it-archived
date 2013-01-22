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
            'dashboardCheck': True,
            'l10nChangesets': 'li',
            'partials': '0',
            'ready': True,
            'complete': True,
            'status': '',
            'promptWaitTime': None,
            'mozillaRelbranch': None,
            'commRelbranch': None,
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetReleaseWithPromptWaitTime(self):
        ret = self.get('/releases/Firefox-2-build1')
        expected = {
            'name': 'Firefox-2-build1',
            'product': 'firefox',
            'submitter': 'joe',
            'version': '2',
            'buildNumber': 1,
            'branch': 'a',
            'mozillaRevision': 'def',
            'dashboardCheck': True,
            'l10nChangesets': 'ja zu',
            'partials': '0,1',
            'ready': True,
            'complete': True,
            'status': '',
            'promptWaitTime': 5,
            'mozillaRelbranch': 'FOO',
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

    def testGetL10n(self):
        ret = self.get('/releases/Firefox-2-build1/l10n')
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(ret.content_type, 'text/plain')
        self.assertEquals(ret.data, 'ja zu')

class TestReleasesView(ViewTest):
    def testMakeReady(self):
        ret = self.post('/releases.html', data='readyReleases=Fennec-4-build4&readyReleases=Fennec-4-build5', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build4').first().ready, True)
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build5').first().ready, True)

    def testDelete(self):
        ret = self.post('/releases.html', data='deleteReleases=Fennec-4-build4', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build4').count(), 0)

    def testDeleteReadyRelease(self):
        ret = self.post('/releases.html', data='deleteReleases=Fennec-1-build1', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteCompletedRelease(self):
        ret = self.post('/releases.html', data='deleteReleases=Thunderbird-2-build2', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteWhileMarkingAsReady(self):
        ret = self.post('/releases.html', data='deleteReleases=Fennec-4-build5&readyReleases=Fennec-4-build5', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

class TestReleaseView(ViewTest):
    def testEditRelease(self):
        data = [
            'fennec-version=1.0',
            'fennec-buildNumber=4',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets={"af":"de"}',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ]
        ret = self.post('/release.html', query_string={'name': 'Fennec-4-build4'}, data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build4').first()
            self.assertEquals(got.version, '1.0')
            self.assertEquals(got.l10nChangesets, '{"af":"de"}')
            self.assertEquals(FennecRelease.query.filter_by(name='Fennec-4-build4').count(), 0)

    def testEditReleaseInvalid(self):
        data = [
            'fennec-version=1.0',
            'fennec-buildNumber=1',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ]
        ret = self.post('/release.html', query_string={'name': 'Fennec-4-build4'}, data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testEditNonExistentRelease(self):
        ret = self.post('/release.html', query_string={'name': 'Fennec-blahblah'}, data='fennec-product=fennec', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 404)

    def testEditReadyRelease(self):
        ret = self.get('/release.html', query_string={'name': 'Thunderbird-2-build2'})
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditCompletedRelease(self):
        ret = self.get('/release.html', query_string={'name': 'Thunderbird-2-build2'})
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditReadyReleasePost(self):
        data = [
            'fennec-version=4',
            'fennec-buildNumber=5',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=BAR',
        ]
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-2-build2'}, data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)

    def testEditCompletedReleasePost(self):
        data = [
            'thunderbird-version=0',
            'thunderbird-buildNumber=2',
            'thunderbird-branch=a',
            'thunderbird-mozillaRevision=abc',
            'thunderbird-commRevision=def',
            'thunderbird-dashboardCheck=y',
            'thunderbird-partials=1.0build1',
            'thunderbird-l10nChangesets=xxxx',
            'thunderbird-product=thunderbird',
            'thunderbird-mozillaRelbranch=',
            'thunderbird-commRelbranch=',
        ]
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-2-build2'}, data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)
