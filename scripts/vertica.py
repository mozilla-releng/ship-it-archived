# pip install vertica-python
from vertica_python import connect
from ConfigParser import SafeConfigParser
import json
import os.path
import sys

configFile = "vertica-config.ini"
if not os.path.isfile(configFile):
        print "Could not find configuration file '" + configFile + "'"
        sys.exit(1)

parser = SafeConfigParser()
parser.read(configFile)

connection = connect({
    'host': parser.get('credentials', 'host'),
    'port': int(parser.get('credentials', 'port')),
    'user': parser.get('credentials', 'user'),
    'password': parser.get('credentials', 'password'),
    'database': parser.get('credentials', 'database')
})


def getPartialJSON(channel):
    query = "SELECT version, SUM(tTotalProfiles) AS ADI FROM fhr_rollups_daily_base WHERE stdchannel='%s' GROUP BY timeEnd,version ORDER BY timeEnd desc, SUM(tTotalProfiles) DESC LIMIT 5" % (channel)
    cur = connection.cursor("dict")
    cur.execute(query)
    return cur.fetchall()


def saveAllPartial(exportFile):
    partialESR = getPartialJSON("esr")
    partialRelease = getPartialJSON("release")
    partialBeta = getPartialJSON("beta")
    full = {"beta": partialBeta, "release": partialRelease, "esr": partialESR}

    with open(exportFile, 'w') as outfile:
        json.dump(full, outfile)

saveAllPartial("partial.json")
