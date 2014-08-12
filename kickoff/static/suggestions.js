function guessBranchFromVersion(name, version) {

    isTB = name.indexOf("thunderbird") > -1;

    if (isTB) {
        // Special case for thunderbird
        base = "releases/comm-"
    } else {
        base = "releases/mozilla-"
    }

    if (version == "") {
        // Empty. Reset the field
        return "";
    }

    // Beta version
    betaRE = /^\d+\.\db\d+$/;
    if (version.match(betaRE) != null) {
        // 32.0b2
        return base + "beta";
    }

    // ESR version
    esrRE = /^(\d+)\.[\d.]*\desr$/;
    esrVersion = version.match(esrRE);
    if (esrVersion != null) {
        // 31.0esr or 31.1.0esr
        return base + "esr" + esrVersion[1];
    }

    // Manage Thunderbird case (Stable release but using an ESR branch)
    if (isTB) {
        tbRE = /^(\d+)\.[\d.]*\d$/;
        tbVersion = version.match(tbRE);
        if (tbVersion != null) {
            // 31.0 or 31.0.1
            return base + "esr" + tbVersion[1];
        }
    }

    versionRE = /^\d+\.\d+$|^\d+\.\d\.\d+$/;
    if (version.match(versionRE) != null) {
        // Probably a release. Can be 31.0 or 32.0.1
        return base + "release";
    }
    return "";
}

function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers, branchElement) {
    versions.sort(function(a, b) {
        return a > b;
    });
    // We need to fire this both when a version is selected
    // from the suggestions and when it is entered manually,
    // so we need this in a named function.
    function populateBuildNumber(version) {
        // If we have a build number for the version we're given, use it!
        if (buildNumbers.hasOwnProperty(version)) {
            buildNumberElement.val(buildNumbers[version]);
        }
    }

    function populateBranch(name, version) {
        branch = guessBranchFromVersion(name, version);
        branchElement.val(branch);
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
        }
    }).focus(function() {
        $(this).autocomplete('search');
    }).change(function() {
        populateBuildNumber(this.value);
        populateBranch(this.name, this.value);
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
