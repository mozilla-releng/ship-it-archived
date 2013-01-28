import datetime
import mock

import pytz

import simplejson as json

from kickoff import app
from kickoff.model import FennecRelease
from kickoff.test.views.base import ViewTest


class TestRequestsAPI(ViewTest):
    def testGetAllReleases(self):
        ret = self.get('/releases')
        expected = {
            'releases': ['Fennec-1-build1', 'Fennec-4-build4',
                         'Fennec-4-build5', 'Firefox-2-build1',
                         'Thunderbird-2-build2']
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
            'submittedAt': pytz.utc.localize(datetime.datetime(2005, 1, 1, 1, 1, 1, 1)).isoformat(),
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
            'submittedAt': pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 6)).isoformat(),
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
        ret = self.post('/releases/Fennec-1-build1', data={'complete': True})
        self.assertEquals(ret.status_code, 200, ret.data)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1-build1').first().complete
            self.assertEquals(got, True)

    def testUpdateStatus(self):
        ret = self.post('/releases/Fennec-1-build1', data={'status': 'omg!'})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1-build1').first().status
            self.assertEquals(got, 'omg!')

    def testGetL10n(self):
        ret = self.get('/releases/Firefox-2-build1/l10n')
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(ret.content_type, 'text/plain')
        self.assertEquals(ret.data, 'ja zu')

    def testResetReady(self):
        data = {'status': 'error!', 'ready': False}
        ret = self.post('/releases/Fennec-1-build1', data=data)
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1-build1').first()
            self.assertEquals(got.ready, False)
            self.assertEquals(got.status, 'error!')

    def testCantMarkasNotReadyAndComplete(self):
        data = {'complete': True, 'ready': False}
        ret = self.post('/releases/Fennec-1-build1', data=data)
        self.assertEquals(ret.status_code, 400)


class TestReleasesView(ViewTest):
    def testMakeReady(self):
        data = 'readyReleases=Fennec-4-build4&readyReleases=Fennec-4-build5'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-4-build4').first().ready
            self.assertEquals(got, True)
            got = FennecRelease.query.filter_by(name='Fennec-4-build5').first().ready
            self.assertEquals(got, True)

    def testDelete(self):
        data = 'deleteReleases=Fennec-4-build4'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            count = FennecRelease.query.filter_by(name='Fennec-4-build4').count()
            self.assertEquals(count, 0)

    def testDeleteReadyRelease(self):
        data = 'deleteReleases=Fennec-1-build1'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteCompletedRelease(self):
        data = 'deleteReleases=Thunderbird-2-build2'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteWhileMarkingAsReady(self):
        data = 'deleteReleases=Fennec-4-build5&readyReleases=Fennec-4-build5'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)


class TestReleaseView(ViewTest):
    def testEditRelease(self):
        data = '&'.join([
            'fennec-version=1.0',
            'fennec-buildNumber=4',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets={"af":"de"}',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ])
        ret = self.post('/release.html', query_string={'name': 'Fennec-4-build4'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build4').first()
            self.assertEquals(got.version, '1.0')
            self.assertEquals(got.l10nChangesets, '{"af":"de"}')
            count = FennecRelease.query.filter_by(name='Fennec-4-build4').count()
            self.assertEquals(count, 0)

    def testEditReleaseInvalid(self):
        data = '&'.join([
            'fennec-version=1.0',
            'fennec-buildNumber=1',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ])
        ret = self.post('/release.html', query_string={'name': 'Fennec-4-build4'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testEditNonExistentRelease(self):
        data = 'fennec-product=fennec'
        qs = {'name': 'Fennec-blahblah'}
        ret = self.post('/release.html', query_string=qs, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 404)

    def testEditReadyRelease(self):
        qs = {'name': 'Thunderbird-2-build2'}
        ret = self.get('/release.html', query_string=qs)
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditCompletedRelease(self):
        qs = {'name': 'Thunderbird-2-build2'}
        ret = self.get('/release.html', query_string=qs)
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditReadyReleasePost(self):
        data = '&'.join([
            'fennec-version=4',
            'fennec-buildNumber=5',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-dashboardCheck=y',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=BAR',
        ])
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-2-build2'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)

    def testEditCompletedReleasePost(self):
        data = '&'.join([
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
        ])
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-2-build2'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)
