import pytz
import simplejson as json
import datetime
import re

from kickoff import config
from kickoff.test.views.base import ViewTest


class TestJSONL10NRequestsAPI(ViewTest):

    def testJsonListRegionsFiles(self):
        ret = self.get('/json/regions/list.html')
        fileList = ret.data
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("fr.json" in fileList)
        self.assertTrue("de.json" in fileList)

    def testJsonListRegionsFilesFr(self):
        ret = self.get('/json/regions/fr.json')
        allLocales = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(allLocales["fr"], "France")
        self.assertEquals(allLocales["de"], "Allemagne")

    def testJsonListRegionsFilesDe(self):
        ret = self.get('/json/regions/de.json')
        allLocales = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertEquals(allLocales["fr"], "Frankreich")
        self.assertEquals(allLocales["de"], "Deutschland")

    def testJsonListl10nFiles(self):
        ret = self.get('/json/l10n/list.html')
        fileList = ret.data
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("Fennec-23.0b2-build4" in fileList)
        self.assertTrue("Thunderbird-24.0b2-build2.json" in fileList)
        self.assertTrue("Firefox-2.0-build1.json" in fileList)
        # Check if we have duplicates of a given beta aggregation
        aggregated_entries = \
            [i for i, htmlLine in enumerate(fileList.split('<br />')) if "Firefox-3.0beta.json" in htmlLine]
        self.assertEquals(len(aggregated_entries), 1)

    def testJsonFileFX(self):
        ret = self.get('/json/l10n/Firefox-2.0-build1.json')
        jsonFx = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("ja" in jsonFx["locales"])
        self.assertEquals(jsonFx["locales"]["ja"]["changeset"], "zu")

        self.assertEquals(jsonFx['submittedAt'], pytz.utc.localize(datetime.datetime(2005, 1, 2, 3, 4, 5, 6)).isoformat())
        self.assertEquals(jsonFx['shippedAt'], pytz.utc.localize(datetime.datetime(2005, 1, 4, 3, 4, 5, 6)).isoformat())

    def testJsonFileFennec(self):
        ret = self.get('/json/l10n/Fennec-24.0-build4.json')
        jsonFx = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("an" in jsonFx["locales"])
        self.assertEquals(jsonFx["locales"]["an"]["changeset"], "fe436c75f71d")

        self.assertEquals(jsonFx['submittedAt'], pytz.utc.localize(datetime.datetime(2015, 2, 26, 3, 4, 5, 6)).isoformat())
        self.assertEquals(jsonFx['shippedAt'], pytz.utc.localize(datetime.datetime(2015, 3, 1, 3, 4, 5, 6)).isoformat())

    def testJsonFileTB(self):
        ret = self.get('/json/l10n/Thunderbird-24.0b2-build2.json')
        jsonFx = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)
        self.assertTrue("yy" in jsonFx["locales"])
        self.assertEquals(jsonFx["locales"]["yy"]["changeset"], "zz")

        self.assertEquals(jsonFx['submittedAt'], pytz.utc.localize(datetime.datetime(2005, 1, 1, 1, 1, 1, 1)).isoformat())
        self.assertEquals(jsonFx['shippedAt'], pytz.utc.localize(datetime.datetime(2005, 2, 1, 1, 1, 1, 1)).isoformat())

    FIREFOX_BETA_3_REGEX = re.compile(r"Firefox-3\.0b\d+-build\d+")

    def testJsonFileBeta(self):
        ret = self.get('/json/l10n/Firefox-3.0beta.json')
        jsonFx = json.loads(ret.data)
        self.assertEquals(ret.status_code, 200)

        beta_releases = jsonFx['releases']
        self.assertEquals(len(beta_releases), 3)
        for beta in beta_releases:
            self.assertTrue(self.FIREFOX_BETA_3_REGEX.match(beta['name']) is not None)
            self.assertTrue('ja' in beta['locales'])
            self.assertTrue('submittedAt' in beta)
            self.assertTrue('shippedAt' in beta)
