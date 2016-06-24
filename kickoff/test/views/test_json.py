import simplejson as json

from kickoff import config
from kickoff.test.views.base import ViewTest


class TestJSONRequestsAPI(ViewTest):

    def testMajorReleases(self):
        ret = self.get('/json/firefox_history_major_releases.json')
        expected = {
            "2.0": "2005-01-04",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecMajorReleases(self):
        ret = self.get('/json/mobile_history_major_releases.json')
        expected = {
            "24.0": "2015-03-01",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdMajorReleases(self):
        ret = self.get('/json/thunderbird_history_major_releases.json')
        expected = {
            "23.0": "2005-01-03",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testStablityReleases(self):
        ret = self.get('/json/firefox_history_stability_releases.json')
        expected = {'2.0.2': '2005-01-04',
                    "3.0.1": "2005-01-02",
                    "38.1.0": "2015-01-04",
                    }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecStableReleases(self):
        ret = self.get('/json/mobile_history_stability_releases.json')
        expected = {
            "24.0.1": "2015-02-26",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdStableReleases(self):
        ret = self.get('/json/thunderbird_history_stability_releases.json')
        expected = {
            "23.0.1": "2014-02-03",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testBetaReleases(self):
        ret = self.get('/json/firefox_history_development_releases.json')
        expected = {
            "3.0b2": "2005-01-02",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testFennecBetaReleases(self):
        ret = self.get('/json/mobile_history_development_releases.json')
        expected = {
            "23.0b2": "2015-02-27",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testThunderbirdBetaReleases(self):
        ret = self.get('/json/thunderbird_history_development_releases.json')
        expected = {
            "24.0b2": "2005-02-01",
        }
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(json.loads(ret.data), expected)

    def testPrimaryBuilds(self):
        ret = self.get('/json/firefox_primary_builds.json')
        primary = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        # I guess we will always have more than 20 locales
        print primary
        self.assertTrue(len(primary) > 20)
        # i guess we will always have french or german
        self.assertTrue('fr' in primary)
        self.assertTrue('de' in primary)
        self.assertTrue('en-US' in primary)
        # but no just en
        self.assertTrue('en' not in primary)

    def testTBPrimaryBuilds(self):
        ret = self.get('/json/thunderbird_primary_builds.json')
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
        ret = self.get('/json/thunderbird_beta_builds.json')
        primary = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)

    def testFirefoxVersions(self):
        config.CURRENT_ESR = "2"
        config.ESR_NEXT = "38"
        config.AURORA_VERSION = "23.0a2"
        config.NIGHTLY_VERSION = "24.0a2"
        ret = self.get('/json/firefox_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(versions['FIREFOX_ESR_NEXT'], "38.1.0esr")
        self.assertEquals(versions['FIREFOX_ESR'], "2.0.2esr")
        self.assertEquals(versions['LATEST_FIREFOX_RELEASED_DEVEL_VERSION'], "3.0b2")
        self.assertEquals(versions['FIREFOX_AURORA'], "23.0a2")
        self.assertEquals(versions['FIREFOX_NIGHTLY'], "24.0a2")
        self.assertEquals(versions['LATEST_FIREFOX_VERSION'], '2.0')
        self.assertEquals(versions['LATEST_FIREFOX_OLDER_VERSION'], "3.6.28")
        self.assertEquals(versions['LATEST_FIREFOX_DEVEL_VERSION'], "3.0b2")
        self.assertTrue("FIREFOX_NIGHTLY" in versions)
        self.assertTrue("FIREFOX_AURORA" in versions)
        self.assertTrue("FIREFOX_ESR" in versions)
        self.assertTrue("FIREFOX_ESR_NEXT" in versions)
        self.assertTrue("LATEST_FIREFOX_DEVEL_VERSION" in versions)
        self.assertTrue("LATEST_FIREFOX_OLDER_VERSION" in versions)
        self.assertTrue("LATEST_FIREFOX_RELEASED_DEVEL_VERSION" in versions)
        self.assertTrue("LATEST_FIREFOX_VERSION" in versions)
        self.assertTrue("LATEST_THUNDERBIRD_VERSION" not in versions)

    def testMobileVersions(self):
        config.CURRENT_ESR = "2"
        config.ESR_NEXT = "38"
        config.NIGHTLY_VERSION = "24.0a2"
        config.AURORA_VERSION = "23.0a2"
        config.IOS_VERSION = "1.1"
        config.IOS_BETA_VERSION = "1.2"
        ret = self.get('/json/mobile_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(versions['nightly_version'], "24.0a2")
        self.assertEquals(versions['alpha_version'], "23.0a2")
        self.assertEquals(versions['beta_version'], "23.0b2")
        self.assertEquals(versions['version'], "24.0")
        self.assertEquals(versions['ios_version'], "1.1")
        self.assertEquals(versions['ios_beta_version'], "1.2")

    def testThunderbirdVersions(self):
        ret = self.get('/json/thunderbird_versions.json')
        versions = json.loads(ret.data)
        print versions
        self.assertEquals(ret.status_code, 200)

        self.assertTrue("LATEST_THUNDERBIRD_VERSION" in versions)
        self.assertEquals(versions['LATEST_THUNDERBIRD_VERSION'], "23.0.1")
        self.assertTrue("LATEST_THUNDERBIRD_DEVEL_VERSION" in versions)
        self.assertEquals(versions['LATEST_THUNDERBIRD_DEVEL_VERSION'], "24.0b2")
        self.assertTrue("FIREFOX_ESR" not in versions)
        self.assertTrue("FIREFOX_ESR_NEXT" not in versions)
        self.assertTrue("LATEST_FIREFOX_DEVEL_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_OLDER_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_RELEASED_DEVEL_VERSION" not in versions)
        self.assertTrue("LATEST_FIREFOX_VERSION" not in versions)

    def testJsonListFiles(self):
        ret = self.get('/json/json_exports.json')
        fileList = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("/json/mobile_versions.json" in fileList)
        self.assertTrue("/json/firefox_history_major_releases.json" in fileList)

    def testJsonListFilesText(self):
        ret = self.get('json_exports.txt')
        fileList = ret.data
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("mobile_versions.json" in fileList)
        self.assertTrue("firefox_history_major_releases.json" in fileList)

    def testFirefox(self):
        ret = self.get('/json/firefox.json')
        firefoxReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(firefoxReleases["version"], 1)
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
        ret = self.get('/json/thunderbird.json')
        thunderbirdReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(thunderbirdReleases["version"], 1)
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
        ret = self.get('/json/mobile_android.json')
        fennecReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(fennecReleases["version"], 1)
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
        ret = self.get('/json/all.json')
        allReleases = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(allReleases["version"], 1)
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
        ret = self.get('/json/firefox_versions.json')
        versions = json.loads(ret.data)

        self.assertEquals(ret.status_code, 200)
        self.assertEquals(versions['FIREFOX_ESR'], "38.1.0esr")
        self.assertEqual(versions["FIREFOX_ESR_NEXT"], "")
