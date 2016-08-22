import textwrap
import copy

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
            'firefox-l10nChangesets=af%20def',
            'firefox-product=firefox',
            'firefox-promptWaitTime=',
            'firefox-mozillaRelbranch=',
            'firefox-mh_changeset=',
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
            self.assertEquals(got.promptWaitTime, None)
            self.assertEquals(got.status, '')
            self.assertEquals(got.mozillaRelbranch, None)
            self.assertEquals(got.mh_changeset, '')

    def testSubmitInvalidForm(self):
        ret = self.post('/submit_release.html', data='fennec-product=fennec', content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 400, ret.data)

    def testSubmitWithWhitespaceInPartials(self):
        data = [
            'firefox-version=9.0',
            'firefox-buildNumber=1',
            'firefox-branch=z',
            'firefox-mozillaRevision=abc',
            'firefox-partials=1.0build1, 1.1build2',
            'firefox-l10nChangesets=af%20def',
            'firefox-product=firefox',
            'firefox-mozillaRelbranch=',
            'firefox-mh_changeset=xyz',
        ]
        ret = self.post('/submit_release.html', data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FirefoxRelease.query.filter_by(name='Firefox-9.0-build1').first()
            self.assertEquals(got.version, '9.0')
            self.assertEquals(got.buildNumber, 1)
            self.assertEquals(got.branch, 'z')
            self.assertEquals(got.mozillaRevision, 'abc')
            self.assertEquals(got.partials, '1.0build1,1.1build2')
            self.assertEquals(got.l10nChangesets, 'af def')
            self.assertEquals(got.ready, False)
            self.assertEquals(got.complete, False)
            self.assertEquals(got.status, '')
            self.assertEquals(got.mozillaRelbranch, None)
            self.assertEquals(got.mh_changeset, 'xyz')

    def testSubmitWithRelbranch(self):
        data = [
            'firefox-version=9.0',
            'firefox-buildNumber=1',
            'firefox-branch=z',
            'firefox-partials=1.0build1, 1.1build2',
            'firefox-l10nChangesets=af%20def',
            'firefox-product=firefox',
            'firefox-mozillaRelbranch=FOO',
        ]
        ret = self.post('/submit_release.html', data='&'.join(data), content_type='application/x-www-form-urlencoded')
        self.assertEquals(ret.status_code, 302, ret.data)
        with app.test_request_context():
            got = FirefoxRelease.query.filter_by(name='Firefox-9.0-build1').first()
            self.assertEquals(got.version, '9.0')
            self.assertEquals(got.buildNumber, 1)
            self.assertEquals(got.branch, 'z')
            self.assertEquals(got.mozillaRevision, 'FOO')
            self.assertEquals(got.partials, '1.0build1,1.1build2')
            self.assertEquals(got.l10nChangesets, 'af def')
            self.assertEquals(got.ready, False)
            self.assertEquals(got.complete, False)
            self.assertEquals(got.status, '')
            self.assertEquals(got.mozillaRelbranch, 'FOO')

    def testSubmitValidVersionNumbers(self):
        valid_versions = (
            '46.0', '46.0.1', '46.2.0', '46.2.1',
            '46.0b1', '46.0b10',
            '46.0esr', '46.0.1esr', '46.2.0esr', '46.2.1esr',
        )
        self._submitAndCheckVersions(valid_versions, 302)

    def testSubmitInvalidVersionNumbers(self):
        invalid_versions = (
            '4', '46', '46.0.0', '46.2', '46.2.0.0',
            '4b1', '46b1', '46.0.0b1', '46.0.1b1', '46.2b1', '46.2.0b1', '46.2.1b1', '46.2.0.0b1',
            '4esr', '46esr', '46.0.0esr', '46.2esr', '46.2.0.0esr',
            '46.0b1esr'
        )
        self._submitAndCheckVersions(invalid_versions, 400)

    def _submitAndCheckVersions(self, versions, expected_status_code):
        BASE_FIELDS = {
            'buildNumber': 1,
            'branch': 'z',
            'l10nChangesets': 'af%20def',
            'mozillaRelbranch': 'FOO',
            'partials': '1.0build1, 1.1build2',
        }

        data = {
            'firefox': copy.deepcopy(BASE_FIELDS),
            'thunderbird': copy.deepcopy(BASE_FIELDS),
            'fennec': copy.deepcopy(BASE_FIELDS),
        }

        data['thunderbird']['commRevision'] = 'zzz'

        del data['fennec']['partials']
        data['fennec']['l10nChangesets'] = '{"hi": { "revision": "fe436c75f71d" }}'

        for product_name in data.keys():
            data[product_name]['product'] = product_name

            for version in versions:
                data[product_name]['version'] = version
                query_tuple = map(
                    lambda values: '%s-%s=%s' % (product_name, values[0], values[1]), data[product_name].items()
                )

                ret = self.post('/submit_release.html', data='&'.join(query_tuple),
                                content_type='application/x-www-form-urlencoded')
                self.assertEquals(ret.status_code, expected_status_code,
                                  'Version "%s" failed' % version)

                if expected_status_code != 302:
                    # Only the version error must pop up, otherwise we may get a false positive test.
                    self.assertTrue(textwrap.dedent("""
   <div id='errors'>
   <ul>

       <li>Version must match either X.0 or X.Y.Z</li>

   </ul>
""") in textwrap.dedent(ret.data), ret.data)
