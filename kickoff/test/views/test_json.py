import re
import simplejson as json

from kickoff import config
from kickoff.test.views.base import ViewTest

JSON_VER = config.JSON_FORMAT_VERSION
BASE_JSON_PATH = '/json/' + JSON_VER

class TestJSONRequestsAPI(ViewTest):

    def testMajorReleases(self):
        ret = self.get(BASE_JSON_PATH + '/firefox_history_major_releases.json')
        expected = {
            "2.0": "2005-01-04",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecMajorReleases(self):
        ret = self.get(BASE_JSON_PATH + '/mobile_history_major_releases.json')
        expected = {
            "24.0": "2015-03-01",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdMajorReleases(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_history_major_releases.json')
        expected = {
            '2.0': '2005-01-03',
            "23.0": "2005-01-03",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testStablityReleases(self):
        ret = self.get(BASE_JSON_PATH + '/firefox_history_stability_releases.json')
        expected = {'2.0.2': '2005-01-04',
                    "3.0.1": "2005-01-02",
                    "38.1.0": "2015-01-04",
                    }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecStableReleases(self):
        ret = self.get(BASE_JSON_PATH + '/mobile_history_stability_releases.json')
        expected = {
            "24.0.1": "2015-02-26",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdStableReleases(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_history_stability_releases.json')
        expected = {
            "23.0.1": "2014-02-03",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testBetaReleases(self):
        ret = self.get(BASE_JSON_PATH + '/firefox_history_development_releases.json')
        expected = {
            "3.0b2": "2005-01-02",
            "3.0b3": "2005-02-03",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecBetaReleases(self):
        ret = self.get(BASE_JSON_PATH + '/mobile_history_development_releases.json')
        expected = {
            "23.0b2": "2015-02-27",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdBetaReleases(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_history_development_releases.json')
        expected = {
            "24.0b2": "2005-02-01",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testPrimaryBuilds(self):
        ret = self.get(BASE_JSON_PATH + '/firefox_primary_builds.json')
        self.assertEquals(ret.status_code, 200)
        primary = json.loads(ret.data)
        # I guess we will always have more than 20 locales
        self.assertTrue(len(primary) > 20)
        # i guess we will always have french or german
        self.assertTrue('fr' in primary)
        self.assertTrue('23.0a2' in primary['fr'])
        self.assertTrue('24.0a1' in primary['fr'])
        self.assertTrue("Windows" in primary['fr']['23.0a2'])
        self.assertTrue("Linux" in primary['fr']['24.0a1'])
        self.assertTrue("OS X" in primary['de']['24.0a1'])
        self.assertEquals(primary['fr']['23.0a2']["Windows"]["filesize"], 0)
        self.assertEquals(primary['fr']['24.0a1']["Windows"]["filesize"], 0)
        self.assertTrue('de' in primary)
        self.assertTrue('en-US' in primary)
        # but no just en
        self.assertTrue('en' not in primary)
        # We will always have Nightly and Aurora builds for French
        self.assertTrue('fr' in config.SUPPORTED_NIGHTLY_LOCALES)
        self.assertTrue('fr' in config.SUPPORTED_AURORA_LOCALES)
        self.assertEquals(len(primary['fr']), 2)
        # We don't have Nightly builds for Acholi but have Aurora builds
        self.assertFalse('ach' in config.SUPPORTED_NIGHTLY_LOCALES)
        self.assertTrue('ach' in config.SUPPORTED_AURORA_LOCALES)
        self.assertEquals(len(primary['ach']), 1)
        # We always have en-US for all channels
        self.assertTrue('23.0a2' in primary['en-US'])
        self.assertTrue('24.0a1' in primary['en-US'])
        self.assertTrue('3.0b3' in primary['en-US'])
        self.assertTrue('3.0.1' in primary['en-US'], primary['en-US'])
        # Verify ESR numbers are well-formed and both esr/esr_next are present
        self.assertTrue('2.0.2esr' in primary['en-US'])
        self.assertTrue('38.1.0esr' in primary['en-US'])
        self.assertEquals(len(primary['en-US']), 6)
        # ja-JP-mac is not a locale we want to expose into product-details
        self.assertFalse('ja-JP-mac' in primary)

    def testPrimaryBuildsDontShowEsrNextIfNonePresent(self):
        config.ESR_NEXT = ''
        ret = self.get(BASE_JSON_PATH + '/firefox_primary_builds.json')
        self.assertEquals(ret.status_code, 200)
        primary_builds = json.loads(ret.data)
        self.assertTrue('2.0.2esr' in primary_builds['en-US'])
        self.assertTrue('38.1.0esr' not in primary_builds['en-US'])

    def testPrimaryBuildsAreSorted(self):
        ret = self.get(BASE_JSON_PATH + '/firefox_primary_builds.json')
        self.assertEquals(ret.status_code, 200)
        givenString = ret.data
        sortedJsonString = json.dumps(json.loads(givenString), sort_keys=True, indent=4)
        self.assertEqual(givenString, sortedJsonString)

    def testTBPrimaryBuilds(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_primary_builds.json')
        primary = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        # I guess we will always have more than 20 locales
        self.assertTrue(len(primary) > 20)
        # i guess we will always have french or german
        self.assertTrue('fr' in primary)
        self.assertTrue('de' in primary)
        self.assertTrue('en-US' in primary)
        # but no just en
        self.assertTrue('en' not in primary)

    def testTBBetaBuilds(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_beta_builds.json')
        primary = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)

    def assertDigitsAndSuffix(self, val, suffix):
        # We don't use assertRegex because it needs Python 2.7.
        # We limit the check on the version number to 2 digits intentionally.
        # Failing on a typo such as 530.a1 is more of a worry than having to
        # update this test when we reach Firefox 100.
        self.assertNotEquals(
            re.match(r'\d\d\.0' + suffix, val),
            None,
            'Version number in config.py is malformed'
        )

    def testFirefoxVersions(self):
        config.CURRENT_ESR = "2"
        config.ESR_NEXT = "38"
        ret = self.get(BASE_JSON_PATH + '/firefox_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)

        self.assertTrue("FIREFOX_ESR_NEXT" in versions)
        self.assertEquals(versions['FIREFOX_ESR_NEXT'], "38.1.0esr")
        self.assertTrue("FIREFOX_ESR" in versions)
        self.assertEquals(versions['FIREFOX_ESR'], "2.0.2esr")
        self.assertTrue("LATEST_FIREFOX_RELEASED_DEVEL_VERSION" in versions)
        self.assertEquals(versions['LATEST_FIREFOX_RELEASED_DEVEL_VERSION'], "3.0b3")
        self.assertTrue("LATEST_FIREFOX_VERSION" in versions)
        self.assertEquals(versions['LATEST_FIREFOX_VERSION'], '3.0.1')
        self.assertTrue("LATEST_FIREFOX_OLDER_VERSION" in versions)
        self.assertEquals(versions['LATEST_FIREFOX_OLDER_VERSION'], "3.6.28")
        self.assertTrue("LATEST_FIREFOX_DEVEL_VERSION" in versions)
        self.assertEquals(versions['LATEST_FIREFOX_DEVEL_VERSION'], "3.0b3")
        self.assertTrue("FIREFOX_NIGHTLY" in versions)
        self.assertDigitsAndSuffix(versions['FIREFOX_NIGHTLY'], 'a1')
        self.assertTrue("FIREFOX_AURORA" in versions)
        self.assertDigitsAndSuffix(versions['FIREFOX_AURORA'], 'a2')

        self.assertTrue("LATEST_THUNDERBIRD_VERSION" not in versions)

    def testMobileVersions(self):
        config.CURRENT_ESR = "2"
        config.ESR_NEXT = "38"
        config.NIGHTLY_VERSION = "24.0a1"
        config.AURORA_VERSION = "23.0a2"
        config.IOS_VERSION = "1.1"
        config.IOS_BETA_VERSION = "1.2"
        ret = self.get(BASE_JSON_PATH + '/mobile_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(versions['nightly_version'], "24.0a1")
        self.assertEquals(versions['alpha_version'], "23.0a2")
        self.assertEquals(versions['beta_version'], "23.0b2")
        self.assertEquals(versions['version'], "24.0.1")
        self.assertEquals(versions['ios_version'], "1.1")
        self.assertEquals(versions['ios_beta_version'], "1.2")

    def testMobileDetails(self):
        config.CURRENT_ESR = "2"
        config.ESR_NEXT = "38"
        config.NIGHTLY_VERSION = "24.0a1"
        config.AURORA_VERSION = "23.0a2"
        config.IOS_VERSION = "1.1"
        config.IOS_BETA_VERSION = "1.2"
        ret = self.get(BASE_JSON_PATH + '/mobile_details.json')
        details = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(details['nightly_version'], "24.0a1")
        self.assertEquals(details['alpha_version'], "23.0a2")
        self.assertEquals(details['beta_version'], "23.0b2")
        self.assertEquals(details['version'], "24.0.1")
        self.assertEquals(details['ios_version'], "1.1")
        self.assertEquals(details['ios_beta_version'], "1.2")
        self.assertTrue("builds" in details)
        self.assertTrue("alpha_builds" in details)
        self.assertTrue("beta_builds" in details)

    def testThunderbirdVersions(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird_versions.json')
        versions = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)

        self.assertTrue("LATEST_THUNDERBIRD_VERSION" in versions)
        self.assertEquals(versions['LATEST_THUNDERBIRD_VERSION'], "23.0.1")
        self.assertTrue("LATEST_THUNDERBIRD_DEVEL_VERSION" in versions)
        self.assertEquals(versions['LATEST_THUNDERBIRD_DEVEL_VERSION'], "24.0b2")
        self.assertTrue("LATEST_THUNDERBIRD_ALPHA_VERSION" in versions)
        self.assertDigitsAndSuffix(versions['LATEST_THUNDERBIRD_ALPHA_VERSION'], 'a2')
        self.assertTrue("LATEST_THUNDERBIRD_NIGHTLY_VERSION" in versions)
        self.assertDigitsAndSuffix(versions['LATEST_THUNDERBIRD_NIGHTLY_VERSION'], 'a1')
        self.assertEquals(len(versions), 4)

        self.assertTrue("FIREFOX_ESR" not in versions)
        self.assertTrue("FIREFOX_ESR_NEXT" not in versions)
        self.assertTrue("LATEST_FIREFOX_DEVEL_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_OLDER_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_RELEASED_DEVEL_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_VERSION" not in versions)

    def testJsonListFiles(self):
        ret = self.get('/json_exports.json')
        fileList = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("/json/" + JSON_VER + "/mobile_versions.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/firefox_history_major_releases.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/l10n/Firefox-3.0beta.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/regions/fr.json" in fileList)

    def testJsonListFilesText(self):
        ret = self.get('/json_exports.txt')
        fileList = ret.data
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("/json/" + JSON_VER + "/mobile_versions.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/firefox_history_major_releases.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/l10n/Firefox-3.0beta.json" in fileList)
        self.assertTrue("/json/" + JSON_VER + "/regions/fr.json" in fileList)

    def testFirefox(self):
        ret = self.get(BASE_JSON_PATH + '/firefox.json')
        firefoxReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        firefoxReleases = firefoxReleases["releases"]
        self.assertTrue("firefox-3.0b2" in firefoxReleases)
        self.assertTrue("firefox-2.0.2esr" in firefoxReleases)
        v = firefoxReleases['firefox-3.0b2']
        self.assertEquals(v['date'], "2005-01-02")
        self.assertEquals(v['version'], "3.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "firefox")
        self.assertEquals(v['is_security_driven'], True)
        self.assertEquals(v['description'], "We did this because of an issue in NSS")
        v = firefoxReleases['firefox-2.0.2esr']
        self.assertEquals(v['date'], "2005-01-04")
        self.assertEquals(v['version'], "2.0.2")
        self.assertEquals(v['category'], "esr")
        self.assertEquals(v['product'], "firefox")
        self.assertEquals(v['is_security_driven'], False)
        self.assertEquals(v['description'], None)

    def testThunderbird(self):
        ret = self.get(BASE_JSON_PATH + '/thunderbird.json')
        thunderbirdReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        thunderbirdReleases = thunderbirdReleases["releases"]
        self.assertTrue("thunderbird-23.0" in thunderbirdReleases)
        self.assertTrue("thunderbird-24.0b2" in thunderbirdReleases)
        v = thunderbirdReleases['thunderbird-23.0']
        self.assertEquals(v['date'], "2005-01-03")
        self.assertEquals(v['version'], "23.0")
        self.assertEquals(v['category'], "major")
        self.assertEquals(v['product'], "thunderbird")
        self.assertEquals(v['is_security_driven'], False)
        self.assertEquals(v['description'], "bar reason")
        v = thunderbirdReleases['thunderbird-24.0b2']
        self.assertEquals(v['date'], "2005-02-01")
        self.assertEquals(v['version'], "24.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "thunderbird")
        self.assertEquals(v['is_security_driven'], False)

    def testFennec(self):
        ret = self.get(BASE_JSON_PATH + '/mobile_android.json')
        fennecReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        fennecReleases = fennecReleases["releases"]
        self.assertTrue("fennec-23.0b2" in fennecReleases)
        self.assertTrue("fennec-24.0" in fennecReleases)
        v = fennecReleases['fennec-23.0b2']
        self.assertEquals(v['date'], "2015-02-27")
        self.assertEquals(v['version'], "23.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "fennec")
        self.assertEquals(v['is_security_driven'], False)
        v = fennecReleases['fennec-24.0']
        self.assertEquals(v['date'], "2015-03-01")
        self.assertEquals(v['version'], "24.0")
        self.assertEquals(v['category'], "major")
        self.assertEquals(v['product'], "fennec")
        self.assertEquals(v['is_security_driven'], False)

    def testAll(self):
        ret = self.get(BASE_JSON_PATH + '/all.json')
        allReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        allReleases = allReleases["releases"]
        self.assertTrue("firefox-3.0b2" in allReleases)
        self.assertTrue("firefox-2.0.2esr" in allReleases)
        v = allReleases['firefox-3.0b2']
        self.assertEquals(v['date'], "2005-01-02")
        self.assertEquals(v['version'], "3.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "firefox")
        self.assertEquals(v['is_security_driven'], True)
        v = allReleases['firefox-2.0.2esr']
        self.assertEquals(v['date'], "2005-01-04")
        self.assertEquals(v['version'], "2.0.2")
        self.assertEquals(v['category'], "esr")
        self.assertEquals(v['product'], "firefox")
        self.assertEquals(v['is_security_driven'], False)

        self.assertTrue("thunderbird-23.0" in allReleases)
        self.assertTrue("thunderbird-24.0b2" in allReleases)
        v = allReleases['thunderbird-23.0']
        self.assertEquals(v['date'], "2005-01-03")
        self.assertEquals(v['version'], "23.0")
        self.assertEquals(v['category'], "major")
        self.assertEquals(v['product'], "thunderbird")
        self.assertEquals(v['is_security_driven'], False)
        v = allReleases['thunderbird-24.0b2']
        self.assertEquals(v['date'], "2005-02-01")
        self.assertEquals(v['version'], "24.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "thunderbird")
        self.assertEquals(v['is_security_driven'], False)

        self.assertTrue("fennec-23.0b2" in allReleases)
        self.assertTrue("fennec-24.0" in allReleases)
        v = allReleases['fennec-23.0b2']
        self.assertEquals(v['date'], "2015-02-27")
        self.assertEquals(v['version'], "23.0b2")
        self.assertEquals(v['category'], "dev")
        self.assertEquals(v['product'], "fennec")
        self.assertEquals(v['is_security_driven'], False)
        v = allReleases['fennec-24.0']
        self.assertEquals(v['date'], "2015-03-01")
        self.assertEquals(v['version'], "24.0")
        self.assertEquals(v['category'], "major")
        self.assertEquals(v['product'], "fennec")
        self.assertEquals(v['is_security_driven'], False)

    def test_esr_next_empty(self):
        config.CURRENT_ESR = "38"
        config.ESR_NEXT = ""
        ret = self.get(BASE_JSON_PATH + '/firefox_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(versions['FIREFOX_ESR'], "38.1.0esr")
        self.assertEqual(versions["FIREFOX_ESR_NEXT"], "")
