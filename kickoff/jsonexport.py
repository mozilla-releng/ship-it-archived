import os
import json

from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from flask import Response

from kickoff import app
from kickoff import config

from flask import jsonify, render_template, make_response

from kickoff.model import getReleases

from kickoff.thunderbirddetails import primary_builds as tb_primary_builds, beta_builds as tb_beta_builds

from mozilla.release.l10n import parsePlainL10nChangesets


def myjsonify(values, detailledJson=False):
    # Transform the structure into a dict
    values = OrderedDict(values)

    if detailledJson:
        # But when this is done on the new json files, it has to be done on
        # the releases member
        valuesToOrder = values["releases"]
    else:
        valuesToOrder = values

    valuesOrdered = OrderedDict(sorted(valuesToOrder.items(), key=lambda x: x[1]))

    if detailledJson:
        values["releases"] = valuesOrdered
    else:
        values = valuesOrdered

    # Don't use jsonsify because jsonify is sorting
    resp = Response(response=json.dumps(values),
                    status=200,
                    mimetype="application/json")
    return(resp)


def generateJSONFileList():
    """ From the flask endpoint, generate a list of json files """
    links = []
    for rule in app.url_map.iter_rules():
        url = str(rule)
        if url.endswith(".json") and "<" not in url:
            links.append((url, os.path.basename(url)))
    return sorted(links)


def getFilteredReleases(product, categories, ESR_NEXT=False, lastRelease=None, withL10N=False, detailledInfo=False):
    version = []
    # we don't export esr in the version name
    if "major" in categories:
        version.append(("major", "([0-9]+\.[0-9]+|14\.0\.1)$"))
    if "stability" in categories:
        version.append(("stability", "([0-9]+\.[0-9]+\.[0-9]+(esr|)$|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(esr|)$)"))
    if "dev" in categories:
        # We had 38.0.5b2
        version.append(("dev", "([0-9]+\.[0-9]|[0-9]+\.[0-9]+\.[0-9])(b|rc|build|plugin)[0-9]+$"))
    if "esr" in categories:
        if ESR_NEXT and not config.ESR_NEXT:
            # No ESR_NEXT yet
            return
        if ESR_NEXT:
            # Ugly hack to manage the next ESR (when we have two overlapping esr)
            version.append(("esr", "(" + config.ESR_NEXT + "\.[0-9]+\.[0-9]+esr$|" + config.ESR_NEXT + "\.[0-9]+\.[0-9]+\.[0-9]+esr$)"))
        else:
            version.append(("esr", "(" + config.CURRENT_ESR + "\.[0-9]+\.[0-9]+esr$|" + config.CURRENT_ESR + "\.[0-9]+\.[0-9]+\.[0-9]+esr$)"))
    releases = getReleases(ready=True, productFilter=product, versionFilterCategory=version, lastRelease=lastRelease)
    results = []
    for r in releases:
        version = r.version.replace("esr", "")
        if r._shippedAt:
            shippedAt = r._shippedAt.strftime("%Y-%m-%d")
        else:
            # No shipped date, we are not interested by this release, skip
            continue

        if withL10N:
            # We need the list of locales
            results.append([version,
                            shippedAt,
                            r.l10nChangesets
                            ])
        else:
            if detailledInfo:
                results.append({"version": version,
                                "shippedAt": shippedAt,
                                "versionDetailled": r.version,
                                "category": r.category,
                                "description": r.description,
                                "isSecurityDriven": r.isSecurityDriven
                                })
            else:
                results.append([version,
                                shippedAt
                                ])
    return results


# Manage firefox_versions.json, thunderbird_versions.json & mobile_versions.json
def returnJSONVersionFile(template, versions):
    response = make_response(render_template(template, versions=versions))
    response.mimetype = "application/json"
    return response


# Firefox JSON


@app.route('/json/firefox_history_major_releases.json', methods=['GET'])
def firefoxHistoryMajorReleasesJson():
    # Match X.Y and 14.0.1 (special case)
    values = getFilteredReleases("firefox", "major")
    return myjsonify(values)


@app.route('/json/firefox_history_stability_releases.json', methods=['GET'])
def firefoxHistoryStabilityReleasesJson():
    # Match X.Y.Z (including esr) + W.X.Y.Z (example 1.5.0.8)
    values = getFilteredReleases("firefox", "stability")
    return myjsonify(values)


@app.route('/json/firefox_history_development_releases.json', methods=['GET'])
def firefoxHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("firefox", "dev")
    return myjsonify(values)


@app.route('/json/firefox_versions.json', methods=['GET'])
def firefoxVersionsJson():

    versions = {
        "FIREFOX_NIGHTLY": config.NIGHTLY_VERSION,
        "FIREFOX_AURORA": config.AURORA_VERSION,
        "LATEST_FIREFOX_OLDER_VERSION": config.LATEST_FIREFOX_OLDER_VERSION,
    }

    # Stable
    lastStable = getFilteredReleases("firefox", ["major", "stability"], lastRelease=True)
    versions['LATEST_FIREFOX_VERSION'] = lastStable[0][0]
    # beta
    lastStable = getFilteredReleases("firefox", ["dev"], lastRelease=True)
    versions['LATEST_FIREFOX_DEVEL_VERSION'] = lastStable[0][0]
    versions['LATEST_FIREFOX_RELEASED_DEVEL_VERSION'] = lastStable[0][0]
    # esr
    lastStable = getFilteredReleases("firefox", ["esr"], lastRelease=True)
    versions['FIREFOX_ESR'] = lastStable[0][0] + "esr"
    # esr next
    lastStable = getFilteredReleases("firefox", ["esr"], lastRelease=True, ESR_NEXT=True)
    if lastStable:
        # If not found, that means that we are managing only a single ESR
        versions['FIREFOX_ESR_NEXT'] = lastStable[0][0] + "esr"

    return returnJSONVersionFile('firefox_versions.json', versions)


def generateLocalizedBuilds(buildsVersionLocales, l10nchangesets, lastVersion):
    # The l10n format for desktop is 'locale changeset'
    # parse it
    locales = parsePlainL10nChangesets(l10nchangesets)
    for localeCode in locales:
        if localeCode not in buildsVersionLocales.keys():
            buildsVersionLocales[localeCode] = [lastVersion]
        else:
            buildsVersionLocales[localeCode] += [lastVersion]

    return buildsVersionLocales


def fillAuroraVersion(buildsVersionLocales):
    for localeCode in config.SUPPORTED_AURORA_LOCALES:
        if localeCode not in buildsVersionLocales.keys():
            buildsVersionLocales[localeCode] = [config.AURORA_VERSION]
        else:
            buildsVersionLocales[localeCode] += [config.AURORA_VERSION]

    return buildsVersionLocales


def updateLocaleWithVersionsTable(product):
    buildsVersionLocales = {}
    # Stable
    lastStable = getFilteredReleases(product, ["major", "stability"],
                                     lastRelease=True, withL10N=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   lastStable[0][2],
                                                   lastStable[0][0])

    # beta
    lastStable = getFilteredReleases(product, ["dev"], lastRelease=True, withL10N=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   lastStable[0][2],
                                                   lastStable[0][0])

    # esr
    lastStable = getFilteredReleases(product, ["esr"], lastRelease=True, withL10N=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   lastStable[0][2],
                                                   lastStable[0][0])
    buildsVersionLocales = fillAuroraVersion(buildsVersionLocales)
    return buildsVersionLocales


@app.route('/json/firefox_primary_builds.json', methods=['GET'])
def firefox_primary_builds_json():
    buildsVersionLocales = updateLocaleWithVersionsTable("firefox")
    return jsonify(buildsVersionLocales)


# Mobile JSON


@app.route('/json/mobile_details.json', methods=['GET'])
@app.route('/json/mobile_versions.json', methods=['GET'])
def mobileDetailsJson():
    versions = {"nightly_version": config.NIGHTLY_VERSION,
                "alpha_version": config.AURORA_VERSION,
                "ios_version": config.IOS_VERSION,
                "ios_beta_version": config.IOS_BETA_VERSION
                }

    lastStable = getFilteredReleases("fennec", ["major", "stability"], lastRelease=True)
    versions['stable'] = lastStable[0][0]

    lastBeta = getFilteredReleases("fennec", ["dev"], lastRelease=True)
    versions['beta_version'] = lastBeta[0][0]
    return returnJSONVersionFile('mobile_versions.json', versions)


@app.route('/json/mobile_history_major_releases.json', methods=['GET'])
def mobileHistoryMajorReleasesJson():
    values = getFilteredReleases("fennec", "major")
    return myjsonify(values)


@app.route('/json/mobile_history_stability_releases.json', methods=['GET'])
def mobileHistoryReleasesJson():
    values = getFilteredReleases("fennec", "stability")
    return myjsonify(values)


@app.route('/json/mobile_history_development_releases.json', methods=['GET'])
def mobileHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("fennec", "dev")
    return myjsonify(values)


# THUNDERBIRD JSON

@app.route('/json/thunderbird_history_major_releases.json', methods=['GET'])
def thunderbirdHistoryMajorReleasesJson():
    values = getFilteredReleases("thunderbird", "major")
    return myjsonify(values)


@app.route('/json/thunderbird_history_stability_releases.json', methods=['GET'])
def thunderbirdHistoryReleasesJson():
    values = getFilteredReleases("thunderbird", "stability")
    return myjsonify(values)


@app.route('/json/thunderbird_history_development_releases.json', methods=['GET'])
def thunderbirdHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("thunderbird", "dev")
    return myjsonify(values)


@app.route('/json/thunderbird_versions.json', methods=['GET'])
def thunderbirdVersionsJson():
    versions = {}
    # Stable
    lastStable = getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)
    versions["LATEST_THUNDERBIRD_VERSION"] = lastStable[0][0]
    # beta
    lastBeta = getFilteredReleases("thunderbird", ["dev"], lastRelease=True)
    versions["LATEST_THUNDERBIRD_DEVEL_VERSION"] = lastBeta[0][0]
    return returnJSONVersionFile('thunderbird_versions.json', versions)


@app.route('/json/thunderbird_primary_builds.json', methods=['GET'])
def thunderbirdPrimaryBuildsJson():
    # default values
    lastStable = getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)
    common = {lastStable[0][0]: {'Windows': {'filesize': 25.1}, 'OS X': {'filesize': 50.8}, 'Linux': {'filesize': 31.8}}}
    tb_prim = {}
    for key in tb_primary_builds:
        tb_prim[key] = common
    return myjsonify(tb_prim)


@app.route('/json/thunderbird_beta_builds.json', methods=['GET'])
def thunderbirdBetaBuildsJson():
    return myjsonify(tb_beta_builds)


@app.route('/json/languages.json', methods=['GET'])
def languagesJson():
    return app.send_static_file('languages.json')


@app.route('/json_exports.html', methods=['GET'])
def jsonExports():
    jsonFiles = generateJSONFileList()
    return render_template('json_exports.html', jsonFiles=jsonFiles)


@app.route('/json/json_exports.json', methods=['GET'])
def jsonExportsJson():
    """ Export the list of files a friendly way to json """
    jsonFiles = generateJSONFileList()
    return myjsonify(jsonFiles)


@app.route('/json_exports.txt', methods=['GET'])
def jsonExportsTxt():
    """ Export the list of files a friendly way to txt """
    jsonFiles = generateJSONFileList()
    response = make_response(render_template("json_exports.txt", jsonFiles=jsonFiles))
    response.mimetype = "text/plain"
    return response


def getReleasesForJson(product):
    releases = getFilteredReleases(product, ["major", "stability", "esr", "dev"], detailledInfo=True)
    release_list = defaultdict()
    for r in releases:
        version = r["versionDetailled"]
        category = "esr" if version.endswith("esr") else r["category"]
        key = "{0}-{1}".format(product, version)
        release_list[key] = {
            "date": r["shippedAt"],
            "version": r["version"],
            "product": product,
            "category": category,
            "description": r["description"],
            "is_security_driven": r["isSecurityDriven"] is True
        }
    release_list = {"version": config.JSON_FORMAT_VERSION,
                    "releases": release_list
                    }
    return release_list


@app.route('/json/firefox.json', methods=['GET'])
def jsonFirefoxExport():
    """ Export all the firefox versions """
    release_list = getReleasesForJson("firefox")
    return myjsonify(release_list, detailledJson=True)


@app.route('/json/mobile_android.json', methods=['GET'])
def jsonFennecExport():
    """ Export all the fennec versions """
    release_list = getReleasesForJson("fennec")
    return myjsonify(release_list, detailledJson=True)


@app.route('/json/thunderbird.json', methods=['GET'])
def jsonThunderbirdExport():
    """ Export all the thunderbird versions """
    release_list = getReleasesForJson("thunderbird")
    return myjsonify(release_list, detailledJson=True)


@app.route('/json/all.json', methods=['GET'])
def jsonAllExport():
    """ Export all the release available in a single file """
    release_list = {
        "version": config.JSON_FORMAT_VERSION,
        "releases": {}
    }
    for release in ("firefox", "fennec", "thunderbird"):
        release_list["releases"].update(getReleasesForJson(release)["releases"])
    return myjsonify(release_list, detailledJson=True)
