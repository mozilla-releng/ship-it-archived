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

function isFirefox(name) {
    return name.indexOf('firefox') > -1;
}

function isFennec(name) {
    return name.indexOf('fennec') > -1;
}

function isTB(name) {
    return name.indexOf('thunderbird') > -1;
}

function getSanitizedVersionString(candidateString) {
    try {
        var version = new Version(candidateString);
        return version.toString();
    } catch (err) {
        if (!(err instanceof InvalidVersionError)) {
            throw err;
        }
        return '';
    }
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

function craftLastReleasesAsPartials(versionString, allPreviousReleasesStrings, nbExpected) {
    var version = new Version(versionString);
    var allPreviousReleases = allPreviousReleasesStrings.map(function(string) {
        return new Version(string);
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
    if (isFennec(productName)) {
        // Fennec doesn't support partials
        return;
    }

    partialElement.val('');

    base = getBaseRepository(productName);

    maximumNumberOfPartials = 0;
    previousReleases =  [];
    partialsADI = [];
    isFxBeta = false;

    betaVersion = version.match(REGEXES.beta);
    if (betaVersion != null && typeof previousBuilds !== 'undefined' && typeof previousBuilds[base + 'beta'] !== 'undefined') {
        previousReleases = previousBuilds[base + 'beta'];
        maximumNumberOfPartials = 3;
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
                previousReleases = previousBuilds[base];
            }
        } else {
            previousReleases = previousBuilds[base + 'release'];
        }

        partialsADI = isCurrentVersionESR ? allPartial.esr : allPartial.release;
        maximumNumberOfPartials = isCurrentVersionESR ? 1 : 3; // 1 for ESR; max of 3 for promotion until we chain tasks instead of group
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

    // When we have the ADI for Firefox Beta or Thunderbird, we can remove
    // this special case
    partials = isTB(productName) || isFxBeta ?
        craftLastReleasesAsPartials(version, previousReleases, 3) :
        // The first partial will always be the previous published release
        craftLastReleasesAsPartials(version, previousReleases, 1);

    // Firefox X.0 releases are published to the beta channel, so generate a partial
    // from the most recent beta build to speed that up
    if (partials.length < maximumNumberOfPartials && isFirefox(productName) && version.match(/^\d+\.0$/)) {
        betaBuilds = previousBuilds[base + 'beta'];
        if (betaBuilds) {
            // we use craftLastReleasesAsPartials() to avoid duplicates
            lastBeta = craftLastReleasesAsPartials(version, betaBuilds, 1);
            partials.unshift(lastBeta);
        } else {
            console.warn('Expected to add a beta release but none were found');
        }
    }

    var i = 0;
    while (partials.length < maximumNumberOfPartials && i < partialsADIVersion.length) {
        newPartial = getVersionWithBuildNumber(partialsADIVersion[i], previousReleases);
        if (newPartial != undefined && partials.indexOf(newPartial) < 0) {
            // Only add when we found a matching version we haven't used already
            partials.push(newPartial);
        }
        i++;
    }

    partialElement.val(partials.join());
    return true;
}

function _getElmoShortName(productName) {
    switch (productName) {
        case 'firefox':
            return 'fx';
        case 'devedition':
            return 'fx';
        case 'thunderbird':
            return 'tb';
        case 'fennec':
            return 'fennec';
        default:
            throw new Error('unsupported product ' + productName);
    }
}

function getElmoUrl(productName, majorVersionNumber) {
    var shortName = _getElmoShortName(productName);

    var url = CONFIG.baseUrls.elmo;
    url += isFennec(productName) ?
        'json-changesets?av=' + shortName + majorVersionNumber +
        '&platforms=android' +
        // TODO Use actual branch instead of mozilla-beta once bug 1280730 lands
        '&multi_android-multilocale_repo=releases/mozilla-beta' +
        '&multi_android-multilocale_rev=default' +
        '&multi_android-multilocale_path=mobile/android/locales/maemo-locales'
        :
        'l10n-changesets?av=' + shortName + majorVersionNumber;
    return url;
}

function _getL10nChangesetsOptsOfNewVersion(productName, versionObject, branchName, revision) {
    var opts = {};
    if (productName === 'thunderbird' || versionObject.majorNumber < 59) {
        opts.url = getElmoUrl(productName, versionObject.majorNumber);
        opts.downloadPlaceholder = 'Elmo';
    } else {
        opts.downloadPlaceholder = 'l10n-changesets.json on hg.mozilla.org';
        var topFolder = productName === 'fennec' ? 'mobile' : 'browser';
        opts.url = getInTreeFileUrl(branchName, revision, topFolder + '/locales/l10n-changesets.json');
    }

    opts.previousBuildWarning = '';
    return opts;
}

function _getPreviousBuildL10nUrl(productName, versionObject) {
    var baseUrl = window.location.origin;
    var stripBuildNumber = true;
    var versionWithoutBuildNumber = versionObject.toString(stripBuildNumber);
    var releaseFullName = [productName, versionWithoutBuildNumber, 'build' + versionObject.buildNumber].join('-');
    return baseUrl + '/releases/' + releaseFullName + '/l10n';
}

function _getL10nChangesetsOptsOfPreviousBuild(productName, versionObject) {
    var opts = {};
    // Deep copy object
    var previousVersion = $.extend(true, {}, versionObject);

    if (versionObject.buildNumber > 1) {
        previousVersion.buildNumber--;
        opts.url = _getPreviousBuildL10nUrl(productName, previousVersion);
    } else if (versionObject.patchNumber) {
        // XX.0.Z Fall back to XX.0 build1
        previousVersion.buildNumber = 1;
        previousVersion.patchNumber = undefined;
        opts.url = _getPreviousBuildL10nUrl(productName, previousVersion);
    } else {
        throw Error('Unsupported condition for previous build');
    }

    opts.downloadPlaceholder = previousVersion.toString();
    opts.previousBuildWarning = 'Changesets copied from ' + previousVersion.toString() +
        '. If you want to not use them, please edit this field.';

    return opts;
}

function _getUrlAndMessages(productName, versionString, buildNumber, branchName, revision) {
    var versionObject = new Version(versionString);
    versionObject.buildNumber = parseInt(buildNumber, 10);
    if (versionObject.patchNumber || versionObject.buildNumber > 1) {
        return _getL10nChangesetsOptsOfPreviousBuild(productName, versionObject);
    } else {
        return _getL10nChangesetsOptsOfNewVersion(productName, versionObject, branchName, revision);
    }
}

function populateL10nChangesets(productName, version, buildNumber, branchName, revision) {
    var changesetsElement = $('#' + productName + '-l10nChangesets');

    if (!version) {
        changesetsElement.val('');
        return;
    }

    var oldPlaceholder = changesetsElement.attr('placeholder');
    var warningElement = changesetsElement.siblings('.help').find('.warning');
    var opts = _getUrlAndMessages(productName, version, buildNumber, branchName, revision);

    changesetsElement.val('');
    changesetsElement.attr('placeholder', 'Trying to download from ' + opts.downloadPlaceholder);
    changesetsElement.prop('disabled', true);
    warningElement.text('');

    $.ajax({
        url: opts.url,
    }).done(function(changesets) {
        if (typeof changesets === 'object') {
            changesets = JSON.stringify(changesets, null, '  ');
        }
        changesetsElement.val(changesets);
        warningElement.text(opts.previousBuildWarning);
    }).fail(function() {
        changesetsElement.val('');
        // Sadly, jQuery.ajax() doesn't return the reason of the error :(
        // http://api.jquery.com/jQuery.ajax/
        warningElement.text('Could not fetch l10n changesets! Are you sure the revision or the version you provided are correct?');
    }).always(function() {
        changesetsElement.prop('disabled', false);
        changesetsElement.attr('placeholder', oldPlaceholder);
    });
}

function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers, branchElement, partialElement, previousBuilds, partialInfo) {

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
        branchElement.trigger('change');
        return branch;
    }

    function populatePartialInfo(productName, version) {
        if (isFennec(productName)) {
            // Fennec doesn't support partials
            return;
        }

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

    function populateAllPossibleFields(productName, rawVersion, buildNumberElement, previousBuilds, partialElement) {
        // TODO show a warning if version is not correct
        var version = getSanitizedVersionString(rawVersion);

        populateBuildNumber(version);
        var buildNumber = buildNumberElement.val();
        var branchName = populateBranch(productName, version);

        populateRevisionWithLatest(productName, branchName);
        populatePartial(productName, version, previousBuilds, partialElement);
        populatePartialInfo(productName, version);

        $('#' + productName + '-mozillaRevision').change(function(event) {
            var revision = $(this).val();
            populateL10nChangesets(productName, version, buildNumber, branchName, revision);
        });

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
            var productName = event.target.name.slice(0, -VERSION_SUFFIX.length);
            populateAllPossibleFields(productName, ui.item.value, buildNumberElement, previousBuilds, partialElement);
        }
    }).focus(function() {
        $(this).autocomplete('search');
    }).change(function() {
        // This setTimeout prevents bug 1339118 from happening. It solves the case where: a version has been picked
        // via `select` and then the form is submit via a click on it. This click triggers a `change` event, which
        // causes some fields (like revision of l10n changesets) to be cleared right before the form is submitted.
        //
        // Putting a setTimeout without a time makes the call to `populateAllPossibleFields()` happen when the event
        // loop is free. Because, submitting a form keeps the event loop busy, `populateAllPossibleFields()` is not
        // called right before the submission.
        setTimeout(function() {
            var productName = this.name.slice(0, -VERSION_SUFFIX.length);
            populateAllPossibleFields(productName, this.value, buildNumberElement, previousBuilds, partialElement);
        }.bind(this));
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
