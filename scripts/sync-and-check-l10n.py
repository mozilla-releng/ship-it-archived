import sys
import os
pathToLib = os.path.join(os.path.dirname(__file__), "../kickoff/")  # NOQA
sys.path.append(pathToLib)  # NOQA
import json
import ConfigParser
import StringIO
import urllib2
from collections import OrderedDict
from config import SUPPORTED_AURORA_LOCALES
from config import SUPPORTED_NIGHTLY_LOCALES


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
        with open(pathToLib + "/static/regions/%s.json" % country, "w") as text_file:
                text_file.write(dump)


def getListLocalesFromURL(URL):
        response = urllib2.urlopen(URL)
        return response.read().splitlines()

enUSURL = "https://hg.mozilla.org/releases/mozilla-aurora/raw-file/tip/toolkit/locales/en-US/chrome/global/regionNames.properties"
saveJSON(enUSURL, "en-US")


listLocaleURL = "https://raw.githubusercontent.com/mozilla-l10n/mozilla-l10n-query/master/app/sources/aurora.txt"
nbLocaleMissing = 0
for loc in getListLocalesFromURL(listLocaleURL):
        url = "https://hg.mozilla.org/releases/l10n/mozilla-aurora/%s/raw-file/tip/toolkit/chrome/global/regionNames.properties" % loc
        saveJSON(url, loc)
        if loc not in SUPPORTED_AURORA_LOCALES:
                nbLocaleMissing = nbLocaleMissing + 1
                print("Warning: '%s' NOT found in SUPPORTED_AURORA_LOCALES" % loc)
print("Sanity check: %d locales not in SUPPORTED_AURORA_LOCALES (my, lo, tsz and wo are expected)" % nbLocaleMissing)

nbLocaleMissing = 0
listLocaleNightlyURL = "https://raw.githubusercontent.com/mozilla-l10n/mozilla-l10n-query/master/app/sources/central.txt"
for loc in getListLocalesFromURL(listLocaleNightlyURL):
        if loc not in SUPPORTED_NIGHTLY_LOCALES:
                nbLocaleMissing = nbLocaleMissing + 1
                print("Warning: '%s' NOT found in SUPPORTED_NIGHTLY_LOCALES" % loc)
print("Sanity check: %d locales not in SUPPORTED_NIGHTLY_LOCALES" % nbLocaleMissing)

print("Note that ship-it IS the source of truth for supported locales")
print("Please report a bug to have a locale added/remove: https://bugzilla.mozilla.org/enter_bug.cgi?product=www.mozilla.org&component=Product%20Details")
