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

function populatePartial(name, version, previousBuilds, partialElement) {

    if (name.indexOf("fennec") > -1) {
        // Android does not need partial
        return true;
    }
    base = getBaseRepository(name);

    nbPartial = 0;
    previousReleases =  [];

    // Beta version
    betaRE = /^\d+\.\db\d+$/;
    betaVersion = version.match(betaRE);
    if (betaVersion != null && typeof previousBuilds !== 'undefined' && typeof previousBuilds[base + 'beta'] !== 'undefined') {
        previousReleases = previousBuilds[base + 'beta'].sort().reverse();
        nbPartial = 3;
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
            previousReleases = previousBuilds[base + 'release'].sort().reverse()
        }
        nbPartial = 4;
    }

    partial = "";
    partialAdded = 0;
    for (i = 0; i < previousReleases.length; i++) {
        // Reuse the previous builds info to generate the partial
        // Strip the build number. "31.0build1" < "31.0.1" => false is JS
        previousRelease = previousReleases[i].replace(/build.*/g, "");
        if (previousRelease < version) {
            // Build a previous release should not occur but it is the case
            // don't provide past partials
            partial += previousReleases[i];

            partialAdded++;

            if (i + 1 != previousReleases.length &&
                partialAdded != nbPartial) {
                // We don't want a trailing ","
                partial += ",";
            }
        }

        if (partialAdded == nbPartial) {
            // We have enough partials. Bye bye.
            break;
        }
    }
    partialElement.val(partial);
    return true;
}


function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers, branchElement, partialElement, previousBuilds, dashboardElement) {

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
