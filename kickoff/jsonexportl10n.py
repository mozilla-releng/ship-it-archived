import os
from collections import defaultdict
from os import path
import json

from flask import render_template

from kickoff import app
from kickoff import config

from mozilla.release.l10n import parsePlainL10nChangesets

from kickoff.model import getReleases
from kickoff.model import getReleaseTable
from jsonexport import myjsonify

@app.route('/json/l10n/<releaseName>.json', methods=['GET'])
def l10nExport(releaseName):
    # Export the l10n changeset for a product
    releaseTable = getReleaseTable(releaseName)
    release = releaseTable.query.filter_by(name=releaseName).first()

    if release is None or release.l10nChangesets == "legacy":
        return myjsonify({})

    locale_list = defaultdict()
    if "Firefox" in releaseName or "Thunderbird" in releaseName:
        locales = parsePlainL10nChangesets(release.l10nChangesets)
        for key, changeset in locales.iteritems():
            locale_list[key] = {
                "changeset": changeset,
            }

    if "Fennec" in releaseName:
        locales = json.loads(release.l10nChangesets)
        for key, extra in locales.iteritems():
            locale_list[key] = {
                "changeset": extra['revision'],
                "platforms": extra['platforms'],
            }

    l10n_list = {"version": config.JSON_FORMAT_L10N_VERSION,
                 "shippedAt": release.shippedAt,
                 "submittedAt": release.submittedAt,
                 "locales": locale_list,
                 }

    return myjsonify(l10n_list)


@app.route('/json/regions/<region>.json', methods=['GET'])
def regionsExport(region):
    # Export a l10n region
    reg = path.join("regions", region + ".json")
    return app.send_static_file(reg)


def generateRegionsJSONFileList():
    # Generate the list of file of regions
    links = []
    reg = path.join(path.dirname(__file__), 'static', 'regions')
    for url in os.listdir(reg):
        if url.endswith(".json"):
            links.append((url, os.path.basename(url)))
    return sorted(links)


@app.route('/json/regions/list.html', methods=['GET'])
def jsonRegionsExports():
    # Export the list generated regions
    jsonFiles = generateRegionsJSONFileList()
    return render_template('regionlist.html', jsonFiles=jsonFiles)


def generateListPerProduct(product):
    releases = getReleases(ready=True, productFilter=product)
    version_list = []
    for r in releases:
        if r._shippedAt and r.l10nChangesets != "legacy":
            # Only list version which shipped with l10n content
            version_list.append(r.name)
    return version_list


@app.route('/json/l10n/list.html', methods=['GET'])
def jsonl10nExports():
    # Export all the l10n available changeset for all products
    version_list = []
    version_list += generateListPerProduct("firefox")
    version_list += generateListPerProduct("fennec")
    version_list += generateListPerProduct("thunderbird")

    return render_template('localeVersionList.html', jsonFiles=version_list)
