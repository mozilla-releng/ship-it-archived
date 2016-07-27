import os
from collections import defaultdict
from os import path
import json
import re

from flask import render_template

from kickoff import app
from kickoff import config

from mozilla.release.l10n import parsePlainL10nChangesets

from kickoff.model import getReleases
from kickoff.model import getReleaseTable
from jsonexportcommon import myjsonify

JSON_VER = str(config.JSON_FORMAT_L10N_VERSION)


@app.route('/json/' + JSON_VER + '/l10n/<releaseName>.json', methods=['GET'])
def l10nExport(releaseName):
    # Export the l10n changeset for a product
    releaseTable = getReleaseTable(releaseName)

    if releaseName.endswith(config.BETA_AGGREGATION_KEYWORD):
        l10n_list = _aggregateBetaLocales(releaseTable, releaseName)
    else:
        l10n_list = _getLocalesByReleaseName(releaseTable, releaseName)

    l10n_list["version"] = config.JSON_FORMAT_L10N_VERSION
    return myjsonify(l10n_list)


def _aggregateBetaLocales(releaseTable, releaseName):
    beta_prefix = releaseName.replace("beta", "b")

    releases = releaseTable.query.filter(releaseTable.name.contains(beta_prefix))
    releases_with_locales = [_getReleaseLocales(release) for release in releases]

    return {
        "releases": releases_with_locales
    }


def _getLocalesByReleaseName(releaseTable, releaseName):
    release = releaseTable.query.filter_by(name=releaseName).first()
    return _getReleaseLocales(release)


def _getReleaseLocales(release):
    if release is None or release.l10nChangesets == config.LEGACY_KEYWORD:
        return myjsonify({})

    locale_list = defaultdict()
    if "Firefox" in release.name or "Thunderbird" in release.name:
        locales = parsePlainL10nChangesets(release.l10nChangesets)
        for key, changeset in locales.iteritems():
            locale_list[key] = {
                "changeset": changeset,
            }

    if "Fennec" in release.name:
        locales = json.loads(release.l10nChangesets)
        for key, extra in locales.iteritems():
            locale_list[key] = {
                "changeset": extra['revision'],
            }

    return {
        "name": release.name,
        "shippedAt": release.shippedAt,
        "submittedAt": release.submittedAt,
        "locales": locale_list,
    }


@app.route('/json/' + JSON_VER + '/regions/<region>.json', methods=['GET'])
def regionsExport(region):
    # Export a l10n region
    reg = path.join("regions", region + ".json")
    return app.send_static_file(reg)

def generateL10NJSONFileList():
    # Export all the l10n available changeset for all products
    version_list = []
    version_list += generateListPerProduct("firefox")
    version_list += generateListPerProduct("fennec")
    version_list += generateListPerProduct("thunderbird")
    return version_list

def generateRegionsJSONFileList():
    # Generate the list of file of regions
    links = []
    reg = path.join(path.dirname(__file__), 'static', 'regions')
    for url in os.listdir(reg):
        if url.endswith(".json"):
            url = '/json/' + JSON_VER + '/regions/' + url
            links.append((url, os.path.basename(url)))
    return sorted(links)


@app.route('/json/' + JSON_VER + '/regions/list.html', methods=['GET'])
def jsonRegionsExports():
    # Export the list generated regions
    jsonFiles = generateRegionsJSONFileList()
    return render_template('regionlist.html', jsonFiles=jsonFiles)


def generateListPerProduct(product):
    releases = getReleases(ready=True, productFilter=product)
    registrar = _L10nReleasesRegistrar()
    for r in releases:
        registrar.addRelease(r)
    return registrar.releases


class _L10nReleasesRegistrar:
    # Matches strings like "Firefox-19.0b1-build1" and stores "Firefox-19.0b"
    BETA_REGEX = re.compile(r"([^\-]+-(\d+\.)+0b)\d+-build\d+")

    def __init__(self):
        self.releases = []
        self._betas_already_processed = set()

    def addRelease(self, release):
        if release.isShippedWithL10n:
            self._addAggregatedBetaOnlyOnce(release)
            self.releases.append(('/json/' + JSON_VER + '/l10n/' + release.name + ".json", release.name))

    def _addAggregatedBetaOnlyOnce(self, release):
        beta_name_match = self.BETA_REGEX.match(release.name)
        if beta_name_match is not None:
            aggregated_base_name = beta_name_match.group(1)
            if aggregated_base_name not in self._betas_already_processed:
                # Remove trailing "b" to add "beta"
                aggregated_full_name = aggregated_base_name[:-1] + 'beta'
                self.releases.append(('/json/' + JSON_VER + '/l10n/' + aggregated_full_name + ".json", aggregated_full_name))
                self._betas_already_processed.add(aggregated_base_name)


@app.route('/json/' + JSON_VER + '/l10n/list.html', methods=['GET'])
def jsonl10nExports():
    version_list = generateL10NJSONFileList()
    return render_template('localeVersionList.html', jsonFiles=version_list)
