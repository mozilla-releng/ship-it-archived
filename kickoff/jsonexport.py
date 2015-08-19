from kickoff import app
from kickoff import config

from flask import jsonify, render_template, make_response

from kickoff.model import getReleases

from kickoff.thunderbirddetails import primary_builds as tb_primary_builds, beta_builds as tb_beta_builds

from mozilla.release.l10n import parsePlainL10nChangesets


def getFilteredReleases(product, categories, ESR_NEXT=False, lastRelease=None, withL10N=False):
    version = []
    # we don't export esr in the version name
    if "major" in categories:
        version.append("([0-9]+\.[0-9]+|14\.0\.1)$")
    if "stability" in categories:
        version.append("([0-9]+\.[0-9]+\.[0-9]+(esr|)$|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(esr|)$)")
    if "dev" in categories:
        # We had 38.0.5b2
        version.append("([0-9]+\.[0-9]|[0-9]+\.[0-9]+\.[0-9])(b|rc|build|plugin)[0-9]+$")
    if "esr" in categories:
        if ESR_NEXT:
            # Ugly hack to manage the next ESR (when we have two overlapping esr)
            version.append("(" + config.ESR_NEXT + "\.[0-9]+\.[0-9]+esr$|" + config.ESR_NEXT + "\.[0-9]+\.[0-9]+\.[0-9]+esr$)")
        else:
            version.append("(" + config.CURRENT_ESR + "\.[0-9]+\.[0-9]+esr$|" + config.CURRENT_ESR + "\.[0-9]+\.[0-9]+\.[0-9]+esr$)")
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
            results.append([version, shippedAt, r.l10nChangesets])
        else:
            results.append([version, shippedAt])

    return results


# Manage firefox_versions.json, thunderbird_versions.json & mobile_versions.json
def returnJSONVersionFile(template, versions):
    response = make_response(render_template(template, versions=versions))
    response.mimetype = "application/json"
    return response


# Firefox JSON


@app.route('/json/firefox_history_major_releases.json', methods=['GET'])
def firefox_history_major_releases_json():
    # Match X.Y and 14.0.1 (special case)
    values = getFilteredReleases("firefox", "major")
    return jsonify(values)


@app.route('/json/firefox_history_stability_releases.json', methods=['GET'])
def firefox_history_stability_releases_json():
    # Match X.Y.Z (including esr) + W.X.Y.Z (example 1.5.0.8)
    values = getFilteredReleases("firefox", "stability")
    return jsonify(values)


@app.route('/json/firefox_history_development_releases.json', methods=['GET'])
def firefox_history_development_releases_json():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("firefox", "dev")
    return jsonify(values)


@app.route('/json/firefox_versions.json', methods=['GET'])
def firefox_versions_json():

    versions = {
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
    versions['FIREFOX_ESR'] = lastStable[0][0]+"esr"
    # esr next
    lastStable = getFilteredReleases("firefox", ["esr"], lastRelease=True, ESR_NEXT=True)
    if lastStable:
        # If not found, that means that we are managing only a single ESR
        versions['FIREFOX_ESR_NEXT'] = lastStable[0][0]+"esr"

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
def mobile_details_json():
    versions = {"alpha_version": config.AURORA_VERSION}

    lastStable = getFilteredReleases("fennec", ["major", "stability"], lastRelease=True)
    versions['stable'] = lastStable[0][0]

    lastBeta = getFilteredReleases("fennec", ["dev"], lastRelease=True)
    versions['beta_version'] = lastBeta[0][0]
    return returnJSONVersionFile('mobile_versions.json', versions)


@app.route('/json/mobile_history_major_releases.json', methods=['GET'])
def mobile_history_major_releases_json():
    values = getFilteredReleases("fennec", "major")
    return jsonify(values)


@app.route('/json/mobile_history_stability_releases.json', methods=['GET'])
def mobile_history_history_releases_json():
    values = getFilteredReleases("fennec", "stability")
    return jsonify(values)


@app.route('/json/mobile_history_development_releases.json', methods=['GET'])
def mobile_history_development_releases_json():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("fennec", "dev")
    return jsonify(values)


# THUNDERBIRD JSON

@app.route('/json/thunderbird_history_major_releases.json', methods=['GET'])
def thunderbird_history_major_releases_json():
    values = getFilteredReleases("thunderbird", "major")
    return jsonify(values)


@app.route('/json/thunderbird_history_stability_releases.json', methods=['GET'])
def thunderbird_history_history_releases_json():
    values = getFilteredReleases("thunderbird", "stability")
    return jsonify(values)


@app.route('/json/thunderbird_history_development_releases.json', methods=['GET'])
def thunderbird_history_development_releases_json():
    # Match 23.b2, 1.0rc2, 3.6.3plugin1 or 3.6.4build7
    values = getFilteredReleases("thunderbird", "dev")
    return jsonify(values)


@app.route('/json/thunderbird_versions.json', methods=['GET'])
def thunderbird_versions_json():
    versions = {}
    # Stable
    lastStable = getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)
    versions["LATEST_THUNDERBIRD_VERSION"] = lastStable[0][0]
    # beta
    lastBeta = getFilteredReleases("thunderbird", ["dev"], lastRelease=True)
    versions["LATEST_THUNDERBIRD_DEVEL_VERSION"] = lastBeta[0][0]
    return returnJSONVersionFile('thunderbird_versions.json', versions)


@app.route('/json/thunderbird_primary_builds.json', methods=['GET'])
def thunderbird_primary_builds_json():
    # default values
    lastStable = getFilteredReleases("thunderbird", ["major", "stability"], lastRelease=True)
    common = {lastStable[0][0]: {'Windows': {'filesize': 25.1}, 'OS X': {'filesize': 50.8}, 'Linux': {'filesize': 31.8}}}
    tb_prim = {}
    for key in tb_primary_builds:
        tb_prim[key] = common
    return jsonify(tb_prim)


@app.route('/json/thunderbird_beta_builds.json', methods=['GET'])
def thunderbird_beta_builds_json():
    return jsonify(tb_beta_builds)


# COMMON JSON

@app.route('/json_exports.html', methods=['GET'])
def json_exports():
    return render_template('json_exports.html')
