import datetime
import random
import string
import unittest

import pytz

import simplejson as json

from kickoff import app, db
from kickoff.model import FennecRelease, ThunderbirdRelease, FirefoxRelease
from kickoff.test.views.base import ViewTest


class TestRequestsAPI(ViewTest):
    maxDiff = None
    def testGetAllReleases(self):
        ret = self.get('/releases')
        expected = {
            'releases': ['Fennec-1.0-build1', 'Fennec-4.0-build4',
                         'Fennec-4.0-build5', 'Fennec-24.0-build4',
                         'Fennec-24.0.1-build4', 'Fennec-23.0b2-build4',
                         'Firefox-2.0-build1', "Firefox-2.0.2esr-build1",
                         'Firefox-38.0esr-build1',
                         'Firefox-3.0b1-build1',
                         'Firefox-3.0b2-build1', 'Firefox-3.0b2-build2',
                         'Firefox-3.0b3-build1',
                         'Firefox-3.0.1-build1',
                         'Devedition-3.0b5-build1',
                         'Thunderbird-2.0-build2', 'Thunderbird-4.0-build1',
                         'Thunderbird-23.0-build1', 'Thunderbird-23.0.1-build1',
                         'Thunderbird-24.0b2-build2'
                     ]
        }
        self.maxDiff = None
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetReadyReleases(self):
        ret = self.get('/releases', query_string={'ready': 1, 'complete': 0})
        expected = {
            'releases': ['Fennec-1.0-build1']
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)


class TestReleaseAPI(ViewTest):
    maxDiff = None

    def testGetRelease(self):
        ret = self.get('/releases/Thunderbird-2.0-build2')
        expected = {
            'name': 'Thunderbird-2.0-build2',
            'product': 'thunderbird',
            'submitter': 'bob',
            'submittedAt': pytz.utc.localize(datetime.datetime(2005, 1, 1, 1, 1, 1, 1)).isoformat(),
            'shippedAt': pytz.utc.localize(datetime.datetime(2005, 1, 3, 1, 1, 1, 1)).isoformat(),
            'version': '2.0',
            'buildNumber': 2,
            'branch': 'b',
            'mozillaRevision': 'ghi',
            'commRevision': 'ghi',
            'comment': 'My great comment!',
            'description': 'we did this release because of bar',
            'isSecurityDriven': True,
            'l10nChangesets': 'li',
            'partials': '0',
            'ready': True,
            'complete': True,
            'starter': None,
            'status': '',
            'promptWaitTime': None,
            'mozillaRelbranch': None,
            'commRelbranch': None,
            'mh_changeset': 'xyz',
            'release_eta': None,
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetReleaseWithPromptWaitTime(self):
        ret = self.get('/releases/Firefox-2.0-build1')
        expected = {
            'name': 'Firefox-2.0-build1',
            'product': 'firefox',
            'submitter': 'joe',
            'submittedAt': pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 6)).isoformat(),
            'version': '2.0',
            'buildNumber': 1,
            'comment': 'yet an other amazing comment',
            'branch': 'a',
            'mozillaRevision': 'def',
            'description': None,
            'isSecurityDriven': False,
            'l10nChangesets': 'ja zu',
            'partials': '0,1',
            'ready': True,
            'shippedAt': pytz.utc.localize(datetime.datetime(2005, 1, 4, 3, 4, 5, 6)).isoformat(),
            'complete': True,
            'starter': None,
            'status': 'shipped',
            'promptWaitTime': 5,
            'mozillaRelbranch': 'FOO',
            'mh_changeset': 'xyz',
            'release_eta': None,
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testGetReleaseWithReleaseEta(self):
        ret = self.get('/releases/Firefox-3.0b1-build1')
        expected = {
            'name': 'Firefox-3.0b1-build1',
            'product': 'firefox',
            'submitter': 'joe',
            'submittedAt': pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 6)).isoformat(),
            'version': '3.0b1',
            'buildNumber': 1,
            'comment': 'Rule with release_eta',
            'branch': 'a',
            'mozillaRevision': 'def',
            'description': 'Rule with release_eta',
            'isSecurityDriven': False,
            'l10nChangesets': 'ja zu',
            'partials': '0,1',
            'ready': True,
            'shippedAt': pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 6)).isoformat(),
            'complete': True,
            'starter': None,
            'status': 'shipped',
            'promptWaitTime': 5,
            'mozillaRelbranch': 'FOO',
            'mh_changeset': None,
            'release_eta': pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 7)).isoformat(),
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testMarkAsComplete(self):
        ret = self.post('/releases/Fennec-1.0-build1', data={'complete': True})
        self.assertEquals(ret.status_code, 200, ret.data)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build1').first().complete
            self.assertEquals(got, True)

    def testUpdateStatus(self):
        ret = self.post('/releases/Fennec-1.0-build1', data={'status': 'omg!'})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build1').first().status
            self.assertEquals(got, 'omg!')

    def testUpdateStatusTruncate(self):
        longStatus = ''.join(random.choice(string.letters) for i in xrange(270))
        ret = self.post('/releases/Fennec-1.0-build1', data={'status': longStatus})
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build1').first().status
            self.assertEquals(got, longStatus[:250])

    def testGetL10n(self):
        ret = self.get('/releases/Firefox-2.0-build1/l10n')
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(ret.content_type, 'text/plain')
        self.assertEquals(ret.data, 'ja zu')

    def testGetL10n404(self):
        ret = self.get('/releases/Firefox-2.0-build99/l10n')
        self.assertEquals(ret.status_code, 404)

    def testGetComment(self):
        ret = self.get('/releases/Firefox-2.0-build1/comment')
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(ret.content_type, 'text/plain')
        self.assertEquals(ret.data, 'yet an other amazing comment')

    def testGetComment404(self):
        ret = self.get('/releases/Firefox-2.0-build99/comment')
        self.assertEquals(ret.status_code, 404)

    def testResetReady(self):
        data = {'status': 'error!', 'ready': False}
        ret = self.post('/releases/Fennec-1.0-build1', data=data)
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build1').first()
            self.assertEquals(got.ready, False)
            self.assertEquals(got.status, 'error!')

    def testCantMarkasNotReadyAndComplete(self):
        data = {'complete': True, 'ready': False}
        ret = self.post('/releases/Fennec-1.0-build1', data=data)
        self.assertEquals(ret.status_code, 400)

    def testChangeDescription(self):
        description = 'New description'
        data = {'description': description, 'isSecurityDriven': False}
        ret = self.post('/releases/Fennec-1.0-build1', data=data)
        self.assertEquals(ret.status_code, 200)

        with app.test_request_context():
            fennec = FennecRelease.query.filter_by(name='Fennec-1.0-build1').first()
            self.assertEquals(description, fennec.description)

    def testCantMarkReleaseAsIncomplete(self):
        with app.test_request_context():
            release = FirefoxRelease('48.0b7build1',
                                     42,
                                     submitter='moz://a',
                                     version='50.0b6',
                                     buildNumber=1,
                                     mozillaRelbranch='',
                                     branch='releases/mozilla-beta',
                                     mozillaRevision='abcdef123456',
                                     l10nChangesets='ach 72c548f97e82')
            release.complete = True

            db.session.add(release)
            db.session.commit()

            data = {'complete': False, 'ready': False}
            ret = self.post('/releases/Firefox-50.0b6-build1', data=data)
            self.assertEquals(ret.status_code, 400)

    def testChangeStatusSimilarShipped(self):
        with app.test_request_context():
            release = FirefoxRelease('48.0b7build1',
                                     42,
                                     submitter='moz://a',
                                     version='50.0b6',
                                     buildNumber=1,
                                     mozillaRelbranch='',
                                     branch='releases/mozilla-beta',
                                     mozillaRevision='abcdef123456',
                                     l10nChangesets='ach 72c548f97e82',
                                     shippedAt=datetime.datetime(2005, 1, 2, 3, 4, 5, 6))
            release.ready = True
            release.complete = True

            db.session.add(release)
            db.session.commit()

            data = {'status': 'shipped'}
            ret = self.post('/releases/Firefox-50.0b6-build1', data=data)
            self.assertEquals(ret.status_code, 400)


class TestReleasesView(ViewTest):
    maxDiff = None
    def testMakeReady(self):
        data = 'readyReleases=Fennec-4.0-build4&readyReleases=Fennec-4.0-build5'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-4.0-build4').first().ready
            self.assertEquals(got, True)
            got = FennecRelease.query.filter_by(name='Fennec-4.0-build5').first().ready
            self.assertEquals(got, True)

    def testDelete(self):
        data = 'deleteReleases=Fennec-4.0-build4'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 200)
        with app.test_request_context():
            count = FennecRelease.query.filter_by(name='Fennec-4.0-build4').count()
            self.assertEquals(count, 0)

    def testDeleteReadyRelease(self):
        data = 'deleteReleases=Fennec-1.0-build1'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteCompletedRelease(self):
        data = 'deleteReleases=Thunderbird-2.0-build2'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testDeleteWhileMarkingAsReady(self):
        data = 'deleteReleases=Fennec-4.0-build5&readyReleases=Fennec-4.0-build5'
        ret = self.post('/releases.html', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)


class TestReleaseView(ViewTest):
    maxDiff = None
    def testEditRelease(self):
        data = '&'.join([
            'fennec-version=1.0',
            'fennec-buildNumber=4',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-l10nChangesets={"af":"de"}',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ])
        ret = self.post('/release.html', query_string={'name': 'Fennec-4.0-build4'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FennecRelease.query.filter_by(name='Fennec-1.0-build4').first()
            self.assertEquals(got.version, '1.0')
            self.assertEquals(got.l10nChangesets, '{"af":"de"}')
            count = FennecRelease.query.filter_by(name='Fennec-4.0-build4').count()
            self.assertEquals(count, 0)

    def testEditReleaseAddRelbranch(self):
        data = '&'.join([
            'thunderbird-version=4.0',
            'thunderbird-buildNumber=1',
            'thunderbird-branch=b',
            'thunderbird-mozillaRevision=yyy',
            'thunderbird-l10nChangesets=yy zz',
            'thunderbird-mozillaRelbranch=',
            'thunderbird-commRelbranch=BAR',
            'thunderbird-partials=1.0build1',
            'thunderbird-promptWaitTime=',
            'thunderbird-product=thunderbird',
        ])
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-4.0-build1'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = ThunderbirdRelease.query.filter_by(name='Thunderbird-4.0-build1').first()
            self.assertEquals(got.commRelbranch, 'BAR')
            self.assertEquals(got.commRevision, 'BAR')

    def testEditReleaseInvalid(self):
        data = '&'.join([
            'fennec-version=1.0',
            'fennec-buildNumber=1',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=',
        ])
        ret = self.post('/release.html', query_string={'name': 'Fennec-4.0-build4'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400)

    def testEditNonExistentRelease(self):
        data = 'fennec-product=fennec'
        qs = {'name': 'Fennec-blahblah'}
        ret = self.post('/release.html', query_string=qs, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 404)

    def testEditReadyRelease(self):
        qs = {'name': 'Thunderbird-2.0-build2'}
        ret = self.get('/release.html', query_string=qs)
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditCompletedRelease(self):
        qs = {'name': 'Thunderbird-2.0-build2'}
        ret = self.get('/release.html', query_string=qs)
        self.assertEquals(ret.status_code, 302)
        self.assertTrue('/releases.html' in ret.location)

    def testEditReadyReleasePost(self):
        data = '&'.join([
            'fennec-version=4.0',
            'fennec-buildNumber=5',
            'fennec-branch=a',
            'fennec-mozillaRevision=abc',
            'fennec-l10nChangesets=xxxx',
            'fennec-product=fennec',
            'fennec-mozillaRelbranch=BAR',
        ])
        ret = self.post('/release.html', query_string={'name': 'Fennec-1.0-build1'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)

    def testEditCompletedReleasePost(self):
        data = '&'.join([
            'thunderbird-version=0',
            'thunderbird-buildNumber=2',
            'thunderbird-branch=a',
            'thunderbird-mozillaRevision=abc',
            'thunderbird-commRevision=def',
            'thunderbird-partials=1.0build1',
            'thunderbird-l10nChangesets=xxxx',
            'thunderbird-product=thunderbird',
            'thunderbird-mozillaRelbranch=',
            'thunderbird-commRelbranch=',
            'thunderbird-description=foo',
        ])
        ret = self.post('/release.html', query_string={'name': 'Thunderbird-2.0-build2'}, data=data, content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 403)

    def testGetEditableFirefoxRelease(self):
        with app.test_request_context():
            release = FirefoxRelease('48.0b7build1',
                                     42,
                                     submitter='moz://a',
                                     version='50.0b6',
                                     buildNumber=1,
                                     mozillaRelbranch='',
                                     branch='releases/mozilla-beta',
                                     mozillaRevision='abcdef123456',
                                     l10nChangesets='ach 72c548f97e82')
            db.session.add(release)
            db.session.commit()

            ret = self.get('/release.html', query_string={'name': 'Firefox-50.0b6-build1'})
            self.assertEqual(ret.status_code, 200)

    def testGetEditableFennecRelease(self):
        with app.test_request_context():
            release = FennecRelease(submitter='moz://a',
                                    version='0',
                                    buildNumber=1,
                                    mozillaRelbranch='',
                                    branch='releases/mozilla-beta',
                                    mozillaRevision='abcdef123456',
                                    l10nChangesets='ach 72c548f97e82')
            db.session.add(release)
            db.session.commit()

            ret = self.get('/release.html', query_string={'name': 'Fennec-0-build1'})
            self.assertEqual(ret.status_code, 200)

    def testGetEditableThunderbirdRelease(self):
        with app.test_request_context():
            release = ThunderbirdRelease('def',
                                         '48.0b7build1',
                                         '',
                                         1,
                                         submitter='moz://a',
                                         version='0',
                                         buildNumber=1,
                                         mozillaRelbranch='',
                                         branch='releases/mozilla-beta',
                                         mozillaRevision='abcdef123456',
                                         l10nChangesets='ach 72c548f97e82')
            db.session.add(release)
            db.session.commit()
            token = self.get('/csrf_token')
            ret = self.get('/release.html', query_string={'name': 'Thunderbird-0-build1'}, headers=token.headers)
            self.assertEqual(ret.status_code, 200, token.headers)

    def testNotFoundRelease(self):
        ret = self.get('/release.html', query_string={'name': 'Firefox-moz://a'})
        self.assertEqual(ret.status_code, 404)

    def testThunderbirdUpdateWithNoCommRevision(self):
        with app.test_request_context():
            release = ThunderbirdRelease('def',
                                         '',
                                         '1.0build1',
                                         42,
                                         submitter='moz://a',
                                         version='0',
                                         buildNumber=1,
                                         mozillaRelbranch='',
                                         branch='releases/mozilla-beta',
                                         mozillaRevision='abcdef123456',
                                         l10nChangesets='ach 72c548f97e82')
            db.session.add(release)
            db.session.commit()

            data = '&'.join(['thunderbird-version=0',
                             'thunderbird-branch=a',
                             'thunderbird-buildNumber=2',
                             'thunderbird-mozillaRevision=abc',
                             'thunderbird-commRevision=',
                             'thunderbird-partials=1.0build1',
                             'thunderbird-l10nChangesets=xxxx',
                             'thunderbird-product=thunderbird',
                             'thunderbird-mozillaRelbranch=',
                             'thunderbird-commRelbranch=',
                             'thunderbird-description=foo'])

            ret = self.post('/release.html', query_string={'name': 'Thunderbird-0-build1'}, data=data, content_type='application/x-www-form-urlencoded')
            self.assertEqual(ret.status_code, 400)


class TestReleasesListAPI(ViewTest):
    uri = '/releases/releaseslist'
    dataTableVersion = '1.9.4'

    def testGetReleases(self):
        params = {
            'iDisplayStart': 0,
            'iDisplayLength': 10,
            'datatableVersion': self.dataTableVersion,
            'complete': 'true',
            'iSortCol_0': 0,
            'mDataProp_0': 'name',
            'sSortDir_0': 'desc',
            'iColumns': 17
        }

        ret = self.get(self.uri, query_string=params)
        self.assertEquals(ret.status_code, 200)

    def testGetReleasesOrderBySubmittedAt(self):
        params = {
            'iDisplayStart': 0,
            'iDisplayLength': 10,
            'datatableVersion': self.dataTableVersion,
            'complete': 'true',
            'iSortCol_0': 0,
            'mDataProp_0': 'submittedAt',
            'sSortDir_0': 'desc',
            'iColumns': 17
        }

        ret = self.get(self.uri, query_string=params)
        self.assertEquals(ret.status_code, 200)

    def testGetReleasesOrderByShippedAt(self):
        params = {
            'iDisplayStart': 0,
            'iDisplayLength': 10,
            'datatableVersion': self.dataTableVersion,
            'complete': 'true',
            'iSortCol_0': 0,
            'mDataProp_0': 'shippedAt',
            'sSortDir_0': 'asc',
            'iColumns': 17
        }

        ret = self.get(self.uri, query_string=params)
        self.assertEquals(ret.status_code, 200)

    def testGetReleasesWithFilter(self):
        with app.test_request_context():
            release = FirefoxRelease('48.0b7build1',
                                     42,
                                     submitter='moz://a',
                                     version='50.0b6',
                                     buildNumber=1,
                                     mozillaRelbranch='',
                                     branch='releases/mozilla-beta',
                                     mozillaRevision='abcdef123456',
                                     l10nChangesets='ach 72c548f97e82',
                                     shippedAt=datetime.datetime(2005, 1, 2, 3, 4, 5, 6))
            release.ready = True
            release.complete = True

            db.session.add(release)
            db.session.commit()

        params = {
            'iDisplayStart': 0,
            'iDisplayLength': 10,
            'datatableVersion': '1.0.0',
            'complete': 'true',
            'ready': 'true',
            'iSortCol_0': 1,
            'bSearchable_1': 'true',
            'mDataProp_1': 'name',
            'sSortDir_0': 'desc',
            'iColumns': 17,
            'sSearch': 'iref'
        }

        ret = self.get(self.uri, query_string=params)
        self.assertEquals(ret.status_code, 200, ret.data)
