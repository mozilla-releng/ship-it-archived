import os

from collections import defaultdict

from kickoff import app
from kickoff import config

from flask import render_template, make_response

from kickoff.model import getReleases

from kickoff.thunderbirddetails import primary_builds as tb_primary_builds, beta_builds as tb_beta_builds

from mozilla.release.l10n import parsePlainL10nChangesets

from jsonexportcommon import jsonify_by_sorting_values, jsonify_by_sorting_keys
from jsonexportl10n import generateRegionsJSONFileList, generateL10NJSONFileList

# typically, these are dot releases that are considered major
SPECIAL_FIREFOX_MAJORS = ['14.0.1']
SPECIAL_THUNDERBIRD_MAJORS = ['14.0.1', '38.0.1']


def patternize_versions(versions):
    if not versions:
        return ""
    return "|" + "|".join([v.replace(r'.', r'\.') for v in versions])


def generateJSONFileList(withL10Nfiles=False):
    """ From the flask endpoint, generate a list of json files """
    links = []
    for rule in app.url_map.iter_rules():
        url = str(rule)
        if url.endswith(".json") and "<" not in url:
            links.append((url, os.path.basename(url)))
    if withL10Nfiles:
        links += generateRegionsJSONFileList()
        links += generateL10NJSONFileList()
    return sorted(links)


def getFilteredReleases(product, categories, esrNext=False, lastRelease=None,
                        withL10N=False, detailledInfo=False,
                        exclude_esr=False):
    version = []
    # we don't export esr in the version name
    if "major" in categories:
        if product == "thunderbird":
            special_majors = patternize_versions(SPECIAL_THUNDERBIRD_MAJORS)
        else:
            special_majors = patternize_versions(SPECIAL_FIREFOX_MAJORS)
        if exclude_esr:
            version.append(("major", r"([0-9]+\.[0-9]+%s)$" % special_majors))
        else:
            version.append(("major", r"([0-9]+\.[0-9]+(esr|)%s)$" % special_majors))
    if "stability" in categories:
        if exclude_esr:
            version.append(("stability", r"([0-9]+\.[0-9]+\.[0-9]+$|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$)"))
        else:
            version.append(("stability", r"([0-9]+\.[0-9]+\.[0-9]+(esr|)$|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(esr|)$)"))
    if "dev" in categories:
        # We had 38.0.5b2
        version.append(("dev", r"([0-9]+\.[0-9]|[0-9]+\.[0-9]+\.[0-9])(b|rc|build|plugin)[0-9]+$"))
    if "esr" in categories:
        if esrNext and not config.ESR_NEXT:
            # No ESR_NEXT yet
            return
        if esrNext:
            # Ugly hack to manage the next ESR (when we have two overlapping esr)
            version.append(("esr", config.ESR_NEXT + r"(\.[0-9]+){1,2}esr$"))
        else:
            version.append(("esr", config.CURRENT_ESR + r"(\.[0-9]+){1,2}esr$"))
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
                                "buildNumber": r.buildNumber,
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
JSON_VER = config.JSON_FORMAT_VERSION
BASE_JSON_PATH = '/json/' + JSON_VER


@app.route(BASE_JSON_PATH + '/firefox_history_major_releases.json', methods=['GET'])
def firefoxHistoryMajorReleasesJson():
    # Match X.Y and 14.0.1 (special case) but not ESR
    values = getFilteredReleases("firefox", "major", exclude_esr=True)
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/firefox_history_stability_releases.json', methods=['GET'])
def firefoxHistoryStabilityReleasesJson():
    # Match X.Y.Z (including esr) + W.X.Y.Z (example 1.5.0.8)
    values = getFilteredReleases("firefox", "stability")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/firefox_history_development_releases.json', methods=['GET'])
def firefoxHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("firefox", "dev")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/firefox_versions.json', methods=['GET'])
def firefoxVersionsJson():

    versions = {
        "FIREFOX_NIGHTLY": config.NIGHTLY_VERSION,
        "LATEST_FIREFOX_OLDER_VERSION": config.LATEST_FIREFOX_OLDER_VERSION,
    }

    # Stable
    releases = getFilteredReleases("firefox", ["major", "stability"], lastRelease=True, exclude_esr=True)
    versions['LATEST_FIREFOX_VERSION'] = releases[0][0]

    # beta
    betas = getFilteredReleases("firefox", ["dev"], lastRelease=True)
    versions['LATEST_FIREFOX_DEVEL_VERSION'] = betas[0][0]
    versions['LATEST_FIREFOX_RELEASED_DEVEL_VERSION'] = betas[0][0]

    # devedition (now based on beta)
    # Most of the time, beta == deveditions but not always ...
    deveditions = getFilteredReleases("devedition", ["dev"], lastRelease=True)
    versions['FIREFOX_DEVEDITION'] = deveditions[0][0]
    # We used to have aurora, not anymore, moving the value to empty
    versions['FIREFOX_AURORA'] = ""

    # esr
    esr_releases = getFilteredReleases("firefox", ["esr"], lastRelease=True)
    versions['FIREFOX_ESR'] = esr_releases[0][0] + "esr"

    # esr next
    esr_next = getFilteredReleases("firefox", ["esr"], lastRelease=True, esrNext=True)
    if esr_next:
        # If not found, that means that we are managing only a single ESR
        versions['FIREFOX_ESR_NEXT'] = esr_next[0][0] + "esr"
    else:
        versions['FIREFOX_ESR_NEXT'] = ""

    return returnJSONVersionFile('firefox_versions.json', versions)


def _generateDummyFileSizeMetaData(lastVersion):
    version = {lastVersion: {}}
    # This is a legacy list. Product details used to provide the filesize for the download page
    # No longer the case but we keep it to keep the compatibility
    oses = ["Windows", "OS X", "Linux"]
    for os_ in oses:
        # We insert filesize to backward compatibility
        version[lastVersion][os_] = {"filesize": 0}
    return version


def generateLocalizedBuilds(buildsVersionLocales, l10nchangesets, lastVersion):
    # The l10n format for desktop is 'locale changeset'
    # parse it
    locales = parsePlainL10nChangesets(l10nchangesets)

    # We don't have an l10n changeset for en-US but we need en-US in the output
    locales['en-US'] = 'abcd123456'

    for localeCode in locales:
        version = _generateDummyFileSizeMetaData(lastVersion)
        if localeCode not in buildsVersionLocales.keys():
            buildsVersionLocales[localeCode] = version
        else:
            buildsVersionLocales[localeCode].update(version)

    return buildsVersionLocales


def fillPrereleaseVersion(buildsVersionLocales, channel='aurora'):
    # Our default values are for Aurora
    locales = config.SUPPORTED_NIGHTLY_LOCALES if channel == 'nightly' else config.SUPPORTED_AURORA_LOCALES
    versionBranch = config.NIGHTLY_VERSION if channel == 'nightly' else config.AURORA_VERSION

    for localeCode in locales:
        # insert the filesize info for backward compa
        version = _generateDummyFileSizeMetaData(versionBranch)
        if localeCode not in buildsVersionLocales.keys():
            buildsVersionLocales[localeCode] = version
        else:
            buildsVersionLocales[localeCode].update(version)

    return buildsVersionLocales


def updateLocaleWithVersionsTable(product):
    buildsVersionLocales = {}
    # Stable
    releases = getFilteredReleases(product, ["major", "stability"],
                                   lastRelease=True, withL10N=True,
                                   exclude_esr=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   releases[0][2],
                                                   releases[0][0])

    # beta
    betas = getFilteredReleases(product, ["dev"], lastRelease=True, withL10N=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   betas[0][2], betas[0][0])

    # devedition (now based on beta)
    # Most of the time, beta == deveditions but not always ...
    if product == 'firefox':
        deveditions = getFilteredReleases("devedition", ["dev"], lastRelease=True, withL10N=True)
        buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                       deveditions[0][2], deveditions[0][0])

    # esr
    esr_releases = getFilteredReleases(product, ["esr"], lastRelease=True, withL10N=True)
    buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                   esr_releases[0][2],
                                                   esr_releases[0][0] + "esr")

    esr_next = getFilteredReleases(product, ["esr"], lastRelease=True, withL10N=True, esrNext=True)
    if esr_next:
        buildsVersionLocales = generateLocalizedBuilds(buildsVersionLocales,
                                                       esr_next[0][2],
                                                       esr_next[0][0] + "esr")

    buildsVersionLocales = fillPrereleaseVersion(buildsVersionLocales, 'aurora')
    buildsVersionLocales = fillPrereleaseVersion(buildsVersionLocales, 'nightly')

    # Backward compatibility: don't expose ja-JP-mac in product-details json API
    del buildsVersionLocales['ja-JP-mac']

    return buildsVersionLocales


@app.route(BASE_JSON_PATH + '/firefox_primary_builds.json', methods=['GET'])
def firefox_primary_builds_json():
    buildsVersionLocales = updateLocaleWithVersionsTable("firefox")
    return jsonify_by_sorting_keys(buildsVersionLocales)


# Mobile JSON

def mobileVersions():
    versions = {
        "nightly_version": config.NIGHTLY_VERSION,
        "alpha_version": config.NIGHTLY_VERSION,  # Aurora is m-c!
        "ios_version": config.IOS_VERSION,
        "ios_beta_version": config.IOS_BETA_VERSION,
        "stable": getFilteredReleases("fennec", ["major", "stability"], lastRelease=True)[0][0],
        "beta_version": getFilteredReleases("fennec", ["dev"], lastRelease=True)[0][0]
    }
    return versions


@app.route(BASE_JSON_PATH + '/mobile_versions.json', methods=['GET'])
def mobileVersionsJson():
    return returnJSONVersionFile('mobile_versions.json', mobileVersions())


@app.route(BASE_JSON_PATH + '/mobile_details.json', methods=['GET'])
def mobileDetailsJson():
    return returnJSONVersionFile('mobile_details.json', mobileVersions())


@app.route(BASE_JSON_PATH + '/mobile_history_major_releases.json', methods=['GET'])
def mobileHistoryMajorReleasesJson():
    values = getFilteredReleases("fennec", "major")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/mobile_history_stability_releases.json', methods=['GET'])
def mobileHistoryReleasesJson():
    values = getFilteredReleases("fennec", "stability")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/mobile_history_development_releases.json', methods=['GET'])
def mobileHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("fennec", "dev")
    return jsonify_by_sorting_values(values)


# THUNDERBIRD JSON

@app.route(BASE_JSON_PATH + '/thunderbird_history_major_releases.json', methods=['GET'])
def thunderbirdHistoryMajorReleasesJson():
    values = getFilteredReleases("thunderbird", "major")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/thunderbird_history_stability_releases.json', methods=['GET'])
def thunderbirdHistoryReleasesJson():
    values = getFilteredReleases("thunderbird", "stability")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/thunderbird_history_development_releases.json', methods=['GET'])
def thunderbirdHistoryDevelopmentReleasesJson():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("thunderbird", "dev")
    return jsonify_by_sorting_values(values)


@app.route(BASE_JSON_PATH + '/thunderbird_versions.json', methods=['GET'])
def thunderbirdVersionsJson():
    versions = {
        "LATEST_THUNDERBIRD_VERSION": getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)[0][0],
        "LATEST_THUNDERBIRD_DEVEL_VERSION": getFilteredReleases("thunderbird", ["dev"], lastRelease=True)[0][0],
        "LATEST_THUNDERBIRD_ALPHA_VERSION": config.LATEST_THUNDERBIRD_ALPHA_VERSION,
        "LATEST_THUNDERBIRD_NIGHTLY_VERSION": config.LATEST_THUNDERBIRD_NIGHTLY_VERSION,
    }
    return jsonify_by_sorting_values(versions)


@app.route(BASE_JSON_PATH + '/thunderbird_primary_builds.json', methods=['GET'])
def thunderbirdPrimaryBuildsJson():
    # default values
    lastStable = getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)
    common = {lastStable[0][0]: {'Windows': {'filesize': 25.1}, 'OS X': {'filesize': 50.8}, 'Linux': {'filesize': 31.8}}}
    tb_prim = {}
    for key in tb_primary_builds:
        tb_prim[key] = common
    return jsonify_by_sorting_values(tb_prim)


@app.route(BASE_JSON_PATH + '/thunderbird_beta_builds.json', methods=['GET'])
def thunderbirdBetaBuildsJson():
    return jsonify_by_sorting_values(tb_beta_builds)


@app.route(BASE_JSON_PATH + '/languages.json', methods=['GET'])
def languagesJson():
    return app.send_static_file('languages.json')


@app.route('/' + JSON_VER + '/json_exports.html', methods=['GET'])
def jsonExports():
    jsonFiles = generateJSONFileList()
    return render_template('json_exports.html', jsonFiles=jsonFiles, json_ver=JSON_VER)


@app.route('/json_exports.json', methods=['GET'])
def jsonExportsJson():
    """ Export the list of files a friendly way to json """
    jsonFiles = generateJSONFileList(withL10Nfiles=True)
    return jsonify_by_sorting_values(jsonFiles)


@app.route('/json_exports.txt', methods=['GET'])
def jsonExportsTxt():
    """ Export the list of files a friendly way to txt """
    jsonFiles = generateJSONFileList(withL10Nfiles=True)
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
            "build_number": r["buildNumber"],
            "category": category,
            "description": r["description"],
            "is_security_driven": r["isSecurityDriven"] is True
        }
    release_list = {"releases": release_list
                    }
    return release_list


@app.route(BASE_JSON_PATH + '/firefox.json', methods=['GET'])
def jsonFirefoxExport():
    """ Export all the firefox versions """
    release_list = getReleasesForJson("firefox")
    return jsonify_by_sorting_values(release_list, detailledJson=True)


@app.route(BASE_JSON_PATH + '/devedition.json', methods=['GET'])
def jsonDeveditionExport():
    """ Export all the devedition versions """
    release_list = getReleasesForJson("devedition")
    return jsonify_by_sorting_values(release_list, detailledJson=True)


@app.route(BASE_JSON_PATH + '/mobile_android.json', methods=['GET'])
def jsonFennecExport():
    """ Export all the fennec versions """
    release_list = getReleasesForJson("fennec")
    return jsonify_by_sorting_values(release_list, detailledJson=True)


@app.route(BASE_JSON_PATH + '/thunderbird.json', methods=['GET'])
def jsonThunderbirdExport():
    """ Export all the thunderbird versions """
    release_list = getReleasesForJson("thunderbird")
    return jsonify_by_sorting_values(release_list, detailledJson=True)


@app.route(BASE_JSON_PATH + '/all.json', methods=['GET'])
def jsonAllExport():
    """ Export all the release available in a single file """
    release_list = {
        "releases": {}
    }
    for release in ("devedition", "firefox", "fennec", "thunderbird"):
        release_list["releases"].update(getReleasesForJson(release)["releases"])
    return jsonify_by_sorting_values(release_list, detailledJson=True)
