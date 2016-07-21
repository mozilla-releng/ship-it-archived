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
from jsonexport import myjsonify


@app.route('/json/l10n/<releaseName>.json', methods=['GET'])
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
    # We need to keep the first "b", so we can look up names like "Firefox-32.0b"
    beta_keyword_length = len(config.BETA_AGGREGATION_KEYWORD) - 1
    betas_substring = releaseName[:-beta_keyword_length]

    releases = releaseTable.query.filter(releaseTable.name.contains(betas_substring))
    releases_with_locales = [_getReleaseLocales(release) for release in releases]

    return {
        "betas": releases_with_locales
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
            self._addAggregatedBetaIfNeeded(release)
            self.releases.append(release.name)

    def _addAggregatedBetaIfNeeded(self, release):
        first_beta_match = self.BETA_REGEX.match(release.name)
        if first_beta_match is not None:
            aggregated_base_name = first_beta_match.group(1)
            if aggregated_base_name not in self._betas_already_processed:
                aggregated_full_name = aggregated_base_name + 'eta'
                self.releases.append(aggregated_full_name)
                # self._betas_already_processed.add(aggregated_base_name)


@app.route('/json/l10n/list.html', methods=['GET'])
def jsonl10nExports():
    # Export all the l10n available changeset for all products
    version_list = []
    version_list += generateListPerProduct("firefox")
    version_list += generateListPerProduct("fennec")
    version_list += generateListPerProduct("thunderbird")

    return render_template('localeVersionList.html', jsonFiles=version_list)
