import sys
import os
pathToLib = os.path.join(os.path.dirname(__file__), "../kickoff/")  # NOQA
sys.path.append(pathToLib)  # NOQA
import json
import ConfigParser
import StringIO
import urllib2
from collections import OrderedDict
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

# Get regionNames.properties for en-US from mozilla-central
enUSURL = "https://hg.mozilla.org/mozilla-central/raw-file/tip/toolkit/locales/en-US/chrome/global/regionNames.properties"
saveJSON(enUSURL, "en-US")

# Get the list of locales on Nightly for desktop
listDesktopNightlyLocalesURL = "https://hg.mozilla.org/mozilla-central/raw-file/default/browser/locales/all-locales"
remoteDesktopNightlyLocalesList = getListLocalesFromURL(listDesktopNightlyLocalesURL)
# Get the list of locales on Nightly for Android
listAndroidNightlyLocalesURL = "https://hg.mozilla.org/mozilla-central/raw-file/default/mobile/android/locales/all-locales"
remoteAndroidNightlyLocalesList = getListLocalesFromURL(listAndroidNightlyLocalesURL)

# Build the list of all locales available on Nightly
remoteNightlyLocalesList = list(set(remoteAndroidNightlyLocalesList + remoteDesktopNightlyLocalesList))
remoteNightlyLocalesList.sort()

warnings = []
missingLocales = []
for locale in remoteNightlyLocalesList:
    try:
        url = "https://hg.mozilla.org/l10n-central/%s/raw-file/tip/toolkit/chrome/global/regionNames.properties" % locale
        saveJSON(url, locale)
        if locale not in SUPPORTED_NIGHTLY_LOCALES:
            missingLocales.append(locale)
    except:
        warnings.append("Warning: regionNames.properties is not available for %s" % locale)
for locale in missingLocales:
    warnings.append("Warning: '%s' NOT found in SUPPORTED_NIGHTLY_LOCALES" % locale)
if warnings:
    print ("\n".join(warnings))
print("Sanity check: %d locales not in SUPPORTED_NIGHTLY_LOCALES (4 expected: trs, tsz, wo, zam)" % len(missingLocales))

print("Note that ship-it IS the source of truth for supported locales")
print("Please report a bug to have a locale added/remove: https://bugzilla.mozilla.org/enter_bug.cgi?product=Release%20Engineering&component=Ship%20It")
