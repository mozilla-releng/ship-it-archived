# pip install vertica-python
import json
import ConfigParser
import StringIO
import urllib2
from collections import OrderedDict


def readConfFile(url):
        print("Synchronizing from " + url)
        response = urllib2.urlopen(url)
        content = response.read()
        ini_str = '[root]\n' + content
        ini_fp = StringIO.StringIO(ini_str)
        config = ConfigParser.RawConfigParser()
        config.readfp(ini_fp)
        return config.items('root')


def saveJSON(url, country):
        countries = readConfFile(url)
        valuesOrdered = OrderedDict(sorted(dict(countries).items(), key=lambda x: x[1]))
        dump = json.dumps(valuesOrdered, indent=4, separators=(',', ': '))

        # Save
        with open("../kickoff/static/regions/%s.json" % country, "w") as text_file:
                text_file.write(dump)

enUSURL = "https://hg.mozilla.org/mozilla-central/raw-file/tip/toolkit/locales/en-US/chrome/global/regionNames.properties"
saveJSON(enUSURL, "en-US")


listLocaleURL = "https://raw.githubusercontent.com/mozilla-l10n/mozilla-l10n-query/master/app/sources/aurora.txt"

response = urllib2.urlopen(listLocaleURL)
for loc in response.read().splitlines():
        url = "https://hg.mozilla.org/releases/l10n/mozilla-aurora/%s/raw-file/tip/toolkit/chrome/global/regionNames.properties" % loc
        saveJSON(url, loc)
