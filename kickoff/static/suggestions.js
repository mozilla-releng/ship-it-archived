function isBeta(version) {
    return doesRegexMatch(version, REGEXES.beta);
}

function isESR(version) {
    return doesRegexMatch(version, REGEXES.esr);
}

function isRelease(version) {
    return doesRegexMatch(version, REGEXES.release);
}

function isTBRelease(version) {
    return doesRegexMatch(version, REGEXES.thunderbird);
}

function isFennec(name) {
    return name.indexOf('fennec') > -1;
}

function isTB(name) {
    return name.indexOf('thunderbird') > -1;
}

function getBaseRepository(name) {

    if (isTB(name)) {
        // Special case for thunderbird
        return 'releases/comm-';
    } else {
        return 'releases/mozilla-';
    }
}

function guessBranchFromVersion(name, version) {

    base = getBaseRepository(name);

    if (version == '') {
        // Empty. Reset the field
        return '';
    }

    if (isBeta(version)) {
        return base + 'beta';
    }

    if (isESR(version) ||
        // Manage Thunderbird case (Stable release but using an ESR branch)
        isTB(name) && isTBRelease(version)) {
        var majorNumber = version.match(REGEXES.majorNumber)[1];
        return base + 'esr' + majorNumber;
    }

    if (isRelease(version)) {
        return base + 'release';
    }
    return '';
}

function addLastVersionAsPartial(versionString, allPreviousReleasesStrings, nbExpected) {
    var version = new Release(versionString);
    var allPreviousReleases = allPreviousReleasesStrings.map(function(string) {
        return new Release(string);
    });

    var validPreviousReleases = allPreviousReleases.filter(function(release) {
        try {
            return release.isStrictlyPreviousTo(version);
        } catch (err) {
            if (err instanceof NotComparableError) {
                return false;
            }
            throw err;
        }
    });

    validPreviousReleases.splice(nbExpected);
    var validPreviousReleasesStrings = validPreviousReleases.map(function(release) {
        return release.toString();
    });

    return validPreviousReleasesStrings;
}

function getVersionWithBuildNumber(version, previousReleases) {
    for (j = 0; j < previousReleases.length; j++) {
        if (previousReleases[j].indexOf(version + 'build') > -1) {
            return previousReleases[j];
        }
    }
    console.warn('Could not find the build number of ' + version + ' from ' + previousReleases);
    return undefined;
}

function partialConsistencyCheck(partialsADI, previousReleases) {
    stripped = [];
    for (i = 0; i < previousReleases.length; i++) {
        stripped[i] = stripBuildNumber(previousReleases[i]).replace('esr','');
    }
    // All partialsADI must be in previousReleases
    for (i = 0; i < partialsADI.length; i++) {
        if ($.inArray(partialsADI[i], stripped) == -1) {
            console.warn('Partial \'' + partialsADI[i] + '\' not found in the previous build list ' + stripped);
            console.warn('This should not happen. That probably means that your instance does not have recent builds. Please report a bug');
        }
    }
}

function stripBuildNumber(release) {
    // Reuse the previous builds info to generate the partial
    // Strip the build number. "31.0build1" < "31.0.1" => false is JS
    return release.replace(/build.*/g, '');
}

function populatePartial(productName, version, previousBuilds, partialElement) {

    partialElement.val('');

    base = getBaseRepository(productName);

    nbPartial = 0;
    previousReleases =  [];
    partialsADI = [];
    isFxBeta = false;

    betaVersion = version.match(REGEXES.beta);
    if (betaVersion != null && typeof previousBuilds !== 'undefined' && typeof previousBuilds[base + 'beta'] !== 'undefined') {
        previousReleases = previousBuilds[base + 'beta'].sort().reverse();
        nbPartial = 3;
        // Copy the global variable
        // For now, this is pretty much useless as we don't have metrics for specific beta
        // Just prepare the code when it is ready
        partialsADI = allPartial.beta;
        isFxBeta = true;
    }

    var isCurrentVersionESR = isESR(version);
    var isCurrentVersionRelease = isRelease(version);

    if (isCurrentVersionRelease || isCurrentVersionESR) {
        if (isTB(productName) || isCurrentVersionESR) {
            // Thunderbird and Fx ESR are using mozilla-esr as branch
            base = guessBranchFromVersion(productName, version);
            if (typeof previousBuilds[base] !== 'undefined') {
                // If the branch is not supported, do not try to access it
                previousReleases = previousBuilds[base].sort().reverse();
            }
        } else {
            previousReleases = previousBuilds[base + 'release'];
        }

        partialsADI = isCurrentVersionESR ? allPartial.esr : allPartial.release;
        nbPartial = isCurrentVersionESR ? 1 : 3; // 1 for ESR; max of 3 for promotion until we chain tasks instead of group
    }

    // Transform the partialsADI datastruct in a single array to
    // simplify processing
    partialsADIVersion = [];
    for (i = 0; i < partialsADI.length; i++) {
        partialsADIVersion[i] = partialsADI[i].version;
    }

    if (previousReleases == null || previousReleases.length == 0) {
        // No previous build. Not much we can do here.
        return false;
    }
    // Check that all partials match a build.
    partialConsistencyCheck(partialsADIVersion, previousReleases);

    partial = [];
    partialAdded = 0;

    // When we have the ADI for Firefox Beta or Thunderbird, we can remove
    // this special case
    if (isTB(productName) || isFxBeta) {
        // No ADI, select the three first
        partial = addLastVersionAsPartial(version, previousReleases, 3);
        partialAdded = 3;
        partialElement.val(partial.join());
        return true;
    } else {
        // The first partial will always be the previous published release
        partial = addLastVersionAsPartial(version, previousReleases, 1);
        partialAdded++;
    }

    for (i = 0; i < partialsADIVersion.length; i++) {
        newPartial = getVersionWithBuildNumber(partialsADIVersion[i], previousReleases);
        if (newPartial != undefined &&
            partial.indexOf(newPartial) < 0) {
            // Only add when we found a matching version we haven't used already
            partial.push(newPartial);
            partialAdded++;
        }

        if (partialAdded == nbPartial) {
            // We have enough partials. Bye bye.
            break;
        }
    }
    partialElement.val(partial.join());
    return true;
}

function _getElmoShortName(productName) {
    switch (productName) {
        case 'firefox':
            return 'fx';
        case 'thunderbird':
            return 'tb';
        case 'fennec':
            return 'fennec';
        default:
            throw new Error('unsupported product ' + productName);
    }
}

function getElmoUrl(productName, version) {
    var branch = guessBranchFromVersion(productName, version);

    var shortName = _getElmoShortName(productName);
    var majorVersion = version.match(REGEXES.majorNumber)[1];

    var BASE_ELMO_URL = 'https://l10n.mozilla.org/shipping';
    var url = BASE_ELMO_URL;
    url += isFennec(productName) ?
        '/json-changesets?av=' + shortName + majorVersion +
        '&platforms=android' +
        '&multi_android-multilocale_repo=' + branch +
        '&multi_android-multilocale_rev=default' +
        '&multi_android-multilocale_path=mobile/android/locales/maemo-locales'
        :
        '/l10n-changesets?av=' + shortName + majorVersion;
    return url;
}

function getPreviousBuildL10nUrl(productName, version, previousBuildNumber) {
    var baseUrl = window.location.origin;
    var releaseFullName = [productName, version, 'build' + previousBuildNumber].join('-');
    return baseUrl + '/releases/' + releaseFullName + '/l10n';
}

function getUrlAndMessages(productName, version, buildNumber) {
    var opts = {
        url: '',
        downloadMessage: 'Trying to download from ',
        previousBuildWarning: '',
    };

    if (buildNumber > 1) {
        var previousBuildNumber = buildNumber - 1;
        var buildString = 'build' + previousBuildNumber;
        opts.url = getPreviousBuildL10nUrl(productName, version, previousBuildNumber);
        opts.downloadMessage += buildString;
        opts.previousBuildWarning = 'Changesets gotten from ' + buildString +
            '. If you want to not use them, please edit this field.';
    } else {
        opts.url = getElmoUrl(productName, version);
        opts.downloadMessage += 'Elmo';
    }

    return opts;
}

function populateL10nChangesets(productName, version, buildNumber) {
    var changesetsElement = $('#' + productName + '-l10nChangesets');

    if (!version) {
        changesetsElement.val('');
        return;
    }

    var warningElement = changesetsElement.next().find('.warning');
    var opts = getUrlAndMessages(productName, version, buildNumber);

    changesetsElement.val(opts.downloadMessage);
    changesetsElement.prop('disabled', true);
    warningElement.text('');

    $.ajax({
        url: opts.url,
    }).done(function(changesets) {
        changesetsElement.val(changesets);
    }).fail(function() {
        changesetsElement.val('');
        // Sadly, jQuery.ajax() doesn't return the reason of the error :(
        // http://api.jquery.com/jQuery.ajax/
        console.error('Could not fetch l10n changesets');
    }).always(function() {
        changesetsElement.prop('disabled', false);
        warningElement.text(opts.previousBuildWarning);
    });
}

function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers, branchElement, partialElement, previousBuilds, dashboardElement, partialInfo) {

    versions.sort(function(a, b) {
        return a > b;
    });

    if (versions.length == 0) {
        console.warn('Empty version suggestions. Empty or too old data?');
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
    function populateBranch(productName, version) {
        var branch = guessBranchFromVersion(productName, version);
        branchElement.val(branch);
    }

    function dashboardCheck(version) {
        // Building a beta, tick the checkbox
        // Due to limitation, we cannot do that for the release
        if (isBeta(version)) {
            dashboardElement.prop('checked', true);
        } else {
            dashboardElement.prop('checked', false);
        }
    }

    function populatePartialInfo(version) {
        if (partialsADI.length == 0 || !isRelease(version)) {
            partialInfo.html('');
            // No ADI available, don't display anything
            return;
        }

        // Format the data for display
        partialString = 'ADI:<br />';
        for (i = 0; i < partialsADI.length; i++) {
            partialString += partialsADI[i].version + ': ' + partialsADI[i].ADI + '<br />';
        }

        partialInfo.html(partialString);
    }

    var VERSION_SUFFIX = '-version';
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
            var fieldName = event.target.name;
            var version = ui.item.value;
            var productName = fieldName.slice(0, -VERSION_SUFFIX.length);

            populateBuildNumber(version);
            var buildNumber = buildNumberElement.val();

            populateBranch(productName, version);
            if (!isFennec(productName)) {
                // There is no notion of partial on fennec
                populatePartial(productName, version, previousBuilds, partialElement);
                populatePartialInfo(version);
            }
            dashboardCheck(version);
            populateL10nChangesets(productName, version, buildNumber);
        }
    }).focus(function() {
        $(this).autocomplete('search');
    }).change(function() {
        var productName = this.name.slice(0, -VERSION_SUFFIX.length);
        var version = this.value;

        populateBuildNumber(version);
        var buildNumber = buildNumberElement.val();

        populateBranch(productName, version);
        populatePartial(productName, version, previousBuilds, partialElement);
        dashboardCheck(version);
        populateL10nChangesets(productName, version, buildNumber);
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
                    this.value = terms.join(', ');
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
        } else {
            revisionElement.removeAttr('placeholder');
            revisionElement.attr('disabled', 'disabled');
        }
    });
    revisionElement.blur(function() {
        if ($(this).val() == '') {
            relbranchElement.removeAttr('disabled');
        } else {
            relbranchElement.removeAttr('placeholder');
            relbranchElement.attr('disabled', 'disabled');
        }
    });
}
