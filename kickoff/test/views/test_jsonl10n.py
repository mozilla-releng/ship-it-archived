import simplejson as json

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
