import requests

from datetime import datetime, date, timedelta
import json
import os
import sys

CRASH_STATS_BASE_URL = "https://crash-stats.mozilla.com/api/"


def getVersions(channel):
    # Query the list of "Current Versions", which is all that crash-stats provides ADI data for
    r = requests.get(CRASH_STATS_BASE_URL + "ProductVersions",
                     params={"active": "true", "product": "Firefox", "build_type": channel},
                     timeout=20)
    versions = [data["version"] for data in r.json().get("hits", [])]
    # Exclude the special "X.0b" versions which provide no ADI
    if channel == "beta":
        versions = [v for v in versions if not v.endswith("b")]
    return versions


def getPartialJSON(channel, timestamp):
    # Query the ADI data for a given channel and day
    versions = getVersions(channel)
    r = requests.get(CRASH_STATS_BASE_URL + "ADI",
                     params={"start_date": timestamp, "end_date": timestamp, "product": "Firefox",
                             "platforms": ["Windows", "Mac OS X", "Linux"], "versions": versions},
                     timeout=20)
    ADI = []
    for data in r.json().get("hits", []):
        # Translate crash-stats handling of the RC case, X.0b99 --> X.0
        # NB: this merges all RC builds together but we can"t do anything about that
        # TODO - check what happens in the UI
        ADI.append({"version": data["version"].replace("b99", ""), "ADI": data["adi_count"]})
    # ship-it expects the data to be in descending-ADI order
    ADI.sort(key=lambda x: x['ADI'], reverse=True)
    return ADI


def getLatestDataset():
    # ADI data is laggy so we work backwards to find the newest available data
    timestamp = date.today()
    limit = timestamp - timedelta(days=7)
    while getPartialJSON("release", timestamp) == []:
        timestamp = timestamp - timedelta(days=1)
        if timestamp <= limit:
            sys.exit("Stale ADI data, giving up")
    return timestamp


def saveAllPartial(exportFile):
    timestamp = getLatestDataset()
    partialESR = getPartialJSON("esr", timestamp)
    partialRelease = getPartialJSON("release", timestamp)
    partialBeta = getPartialJSON("beta", timestamp)
    lastUpdate = "%s using %s ADI data" % (datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                                           timestamp.strftime("%d/%m/%Y"))
    full = {"beta": partialBeta, "release": partialRelease, "esr": partialESR, "lastUpdate": lastUpdate}

    with open(exportFile + '.tmp', "w") as outfile:
        json.dump(full, outfile)
    os.rename(exportFile + '.tmp', exportFile)

if __name__ == "__main__":
    saveAllPartial("partial.json")
