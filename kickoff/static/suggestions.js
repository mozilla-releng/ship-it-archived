function isBeta(version) {
    // Beta version
    betaRE = /^\d+\.\db\d+$/;
    if (version.match(betaRE) != null) {
        // 32.0b2
        return true;
    }
    return false;
}

function isESR(version) {
    // ESR version
    esrRE = /^(\d+)\.[\d.]*\desr$/;
    esrVersion = version.match(esrRE);
    if (esrVersion != null) {
        // 31.0esr or 31.1.0esr
        return true;
    }
    return false;
}

function isRelease(version) {
    versionRE = /^\d+\.\d+$|^\d+\.\d\.\d+$/;
    if (version.match(versionRE) != null) {
        // Probably a release. Can be 31.0 or 32.0.1
        return true;
    }
    return false;
}

function isTBRelease(version) {
    tbRE = /^(\d+)\.[\d.]*\d$/;
    tbVersion = version.match(tbRE);
    if (tbVersion != null) {
        // 31.0 or 31.0.1
        return true;
    }
    return false;
}

function isTB(name) {
    return name.indexOf("thunderbird") > -1;
}

function getBaseRepository(name) {

    if (isTB(name)) {
        // Special case for thunderbird
        return "releases/comm-"
    } else {
        return "releases/mozilla-"
    }
}

function guessBranchFromVersion(name, version) {

    base = getBaseRepository(name);

    if (version == "") {
        // Empty. Reset the field
        return "";
    }

    // Beta version
    if (isBeta(version)) {
        // 32.0b2
        return base + "beta";
    }

    // ESR version
    if (isESR(version)) {
        // 31.0esr or 31.1.0esr
        return base + "esr" + esrVersion[1];
    }

    // Manage Thunderbird case (Stable release but using an ESR branch)
    if (isTB(name)) {
        if (isTBRelease(version)) {
            // 31.0 or 31.0.1
            return base + "esr" + tbVersion[1];
        }
    }

    if (isRelease(version)) {
        // Probably a release. Can be 31.0 or 32.0.1
        return base + "release";
    }
    return "";
}

function addLastVersionAsPartial(version, previousReleases, nb) {
    partialList=""
    nbAdded=0
    // We always add the last released version to the list
    for (k = 0; k < previousReleases.length; k++) {
        previousRelease = stripBuildNumber(previousReleases[k]);
        if (previousRelease < version) {
            partialList += previousReleases[k] + ",";
            nbAdded++;
            if (nb == nbAdded) {
                return partialList;
            }
        }
    }
}

function getVersionWithBuildNumber(version, previousReleases) {
    for (j = 0; j < previousReleases.length; j++) {
        if (previousReleases[j].indexOf(version) > -1) {
            return previousReleases[j];
        }
    }
    console.warn("Could not find the build number of " + version + " from " + previousReleases);
}


function partialConsistencyCheck(partialsADI, previousReleases) {
    stripped=[]
    for (i = 0; i < previousReleases.length; i++) {
        stripped[i]=stripBuildNumber(previousReleases[i]).replace("esr","");
    }
    // All partialsADI must be in previousReleases
    for (i = 0; i < partialsADI.length; i++) {
        if ($.inArray(partialsADI[i], stripped) == -1) {
            console.warn("Partial '" + partialsADI[i] + "' not found in the previous build list " + stripped);
            console.warn("This should not happen. That probably means that your instance does not have recent builds. Please report a bug");
        }
    }
}


function stripBuildNumber(release) {
    // Reuse the previous builds info to generate the partial
    // Strip the build number. "31.0build1" < "31.0.1" => false is JS
    return release.replace(/build.*/g, "");
}


function populatePartial(name, version, previousBuilds, partialElement) {

    partialElement.val("");
    if (name.indexOf("fennec") > -1) {
        // Android does not need partial
        return true;
    }
    base = getBaseRepository(name);

    nbPartial = 0;
    previousReleases =  [];
    partialsADI = [];

    // Beta version
    betaRE = /^\d+\.\db\d+$/;
    betaVersion = version.match(betaRE);
    if (betaVersion != null && typeof previousBuilds !== 'undefined' && typeof previousBuilds[base + 'beta'] !== 'undefined') {
        previousReleases = previousBuilds[base + 'beta'].sort().reverse();
        nbPartial = 3;
        // Copy the global variable
        // For now, this is pretty much useless as we don't have metrics for specific beta
        partialsADI = allPartial.beta;
    }

    // Release version
    versionRE = /^\d+\.\d+$|^\d+\.\d\.\d+|^\d+\.[\d.]*\desr$/;
    releaseVersion = version.match(versionRE);
    if (releaseVersion != null) {
        if (isTB(name) || isESR(version)) {
            // Thunderbird and Fx ESR are using mozilla-esr as branch
            base = guessBranchFromVersion(name, version);
            if (typeof previousBuilds[base] !== "undefined") {
                // If the branch is not supported, do not try to access it
                previousReleases = previousBuilds[base].sort().reverse()
            }
        } else {
            previousReleases = previousBuilds[base + 'release'];
        }

        if (isESR(version)) {
            // Use the ESR partial
            partialsADI = allPartial.esr;
        } else {
            partialsADI = allPartial.release;
        }
        // For thunderbird, use only the four last

        nbPartial = 4;
    }

    // Transform the partialsADI datastruct in a single array to
    // simplify processing
    partialsADIVersion = [];
    for (i = 0; i < partialsADI.length; i++) {
        partialsADIVersion[i] = partialsADI[i].version;
    }

    if (previousReleases.length == 0) {
        // No previous build. Not much we can do here.
        return false;
    }
    // Check that all partials match a build.
    partialConsistencyCheck(partialsADIVersion, previousReleases);

    partial = "";
    partialAdded = 0;

    if (isTB(name)) {
        // No ADI, select the three first
        partial = addLastVersionAsPartial(version, previousReleases, 3);
        partialAdded=3;
        // Remove the last ","
        partial=partial.slice(0,-1);
        partialElement.val(partial);
        return true;
    } else {
        // The first partial will always be the previous published release
        partial = addLastVersionAsPartial(version, previousReleases, 1);
        partialAdded++;
    }

    for (i = 0; i < partialsADIVersion.length; i++) {

        if (partial.indexOf(partialsADIVersion[i]) > -1) {
            // We have already this version in the list of partial
            // Go to the next one
            continue;
        }
        // Build a previous release should not occur but it is the case
        // don't provide past partials
        partial += getVersionWithBuildNumber(partialsADIVersion[i], previousReleases);
        partialAdded++;

        if (i + 1 != partialsADIVersion.length &&
            partialAdded != nbPartial) {
            // We don't want a trailing ","
            partial += ",";
        }
        if (partialAdded == nbPartial) {
            // We have enough partials. Bye bye.
            break;
        }
    }
    partialElement.val(partial);
    return true;
}


function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers, branchElement, partialElement, previousBuilds, dashboardElement, partialInfo) {

    versions.sort(function(a, b) {
        return a > b;
    });

    if (versions.length == 0) {
        console.warn("Empty version suggestions. Empty or too old data?")
    }

    // We need to fire this both when a version is selected
    // from the suggestions and when it is entered manually,
    // so we need this in a named function.
    function populateBuildNumber(version) {
        // If we have a build number for the version we're given, use it!
        if (buildNumbers.hasOwnProperty(version)) {
            buildNumberElement.val(buildNumbers[version]);
        }
    }

    // From the version, try to guess the branch
    function populateBranch(name, version) {
        branch = guessBranchFromVersion(name, version);
        branchElement.val(branch);
    }

    function dashboardCheck(version) {
        // Building a beta, tick the checkbox
        // Due to limitation, we cannot do that for the release
        if (isBeta(version)) {
            dashboardElement.prop("checked", true);
        } else {
            dashboardElement.prop("checked", false);
        }
    }

    function populatePartialInfo(version) {
        if (partialsADI.length == 0 || !isRelease(version)) {
            partialInfo.html("");
            // No ADI available, don't display anything
            return;
        }

        // Format the data for display
        partialString = "ADI:<br />";
        for (i = 0; i < partialsADI.length; i++) {
            partialString += partialsADI[i].version + ": " + partialsADI[i].ADI + "<br />";
        }

        partialInfo.html(partialString);
    }

    versionElement.autocomplete({
        source: versions,
        minLength: 0,
        delay: 0,
        // Put the autocomplete drop down to the right of the field, unless
        // that would cause horizontal scrolling.
        position: {
            my: 'left',
            at: 'right',
            of: versionElement,
            collision: 'flipfit',
        },
        select: function(event, ui) {
            populateBuildNumber(ui.item.value);
            populateBranch(event.target.name, ui.item.value);
            populatePartial(event.target.name, ui.item.value, previousBuilds, partialElement);
            dashboardCheck(ui.item.value);
            populatePartialInfo(ui.item.value);
        }
    }).focus(function() {
        $(this).autocomplete('search');
    }).change(function() {
        populateBuildNumber(this.value);
        populateBranch(this.name, this.value);
        populatePartial(this.name, this.value, previousBuilds, partialElement);
        dashboardCheck(this.value);
    });
}

function setupBranchSuggestions(branchElement, branches, partialsElement, partials) {
    branches.sort(function(a, b) {
        return a > b;
    });
    branchElement.autocomplete({
        source: branches,
        minLength: 0,
        delay: 0,
        position: {
            my: 'left',
            at: 'right',
            of: branchElement,
            collision: 'flipfit',
        },
    }).focus(function() {
        $(this).autocomplete('search');
    });
    // Not all types of releases can have partials
    if (partialsElement != null) {
        // We don't know what partials we want until the branch is selected,
        // so all of the partials autocomplete setup needs to be done after
        // branch is selected/entered.
        // Most of this is taken directly from the jquery-ui example at:
        // http://jqueryui.com/autocomplete/#multiple
        function populatePartials(branch) {
            partialsElement.autocomplete({
                source: function(request, response) {
                    var suggestions = partials[branch];
                    suggestions.sort(function(a, b) {
                        return a > b;
                    });
                    response($.ui.autocomplete.filter(
                        suggestions, extractLast(request.term)
                    ));
                },
                minLength: 0,
                delay: 0,
                position: {
                    my: 'left',
                    at: 'right',
                    of: partialsElement,
                    collision: 'flipfit',
                },
                select: function(event, ui) {
                    var terms = this.value.split(/,\s*/);
                    terms.pop();
                    terms.push(ui.item.value);
                    this.value = terms.join(", ");
                    return false;
                }
            }).focus(function() {
                $(this).autocomplete('search');
                // prevent value inserted on focus
                return false;
            });
        }
        branchElement.on('autocompleteselect', function(event, ui) {
            populatePartials(ui.item.value);
        });
        branchElement.on('autocompletechange', function() {
            populatePartials(this.value);
        });
    }
}

function extractLast(term) {
    return term.split(/,\s*/).pop();
}

function setupRevisionDisabling(relbranchElement, revisionElement) {
    relbranchElement.blur(function() {
        if ($(this).val() == '') {
            revisionElement.removeAttr('disabled');
            revisionElement.attr('placeholder', 'abcdef123456');
        }
        else {
            revisionElement.removeAttr('placeholder');
            revisionElement.attr('disabled', 'disabled');
        }
    });
    revisionElement.blur(function() {
        if ($(this).val() == '') {
            relbranchElement.removeAttr('disabled');
        }
        else {
            relbranchElement.removeAttr('placeholder');
            relbranchElement.attr('disabled', 'disabled');
        }
    });
}
