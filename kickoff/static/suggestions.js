function setupVersionSuggestions(versionElement, versions, buildNumberElement, buildNumbers) {
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
        // If not, it's probably "1"
        else {
            buildNumberElement.val('1');
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
            collision: 'flip',
        },
        select: function(event, ui) {
            populateBuildNumber(ui.item.value);
        }
    }).focus(function() {
        $(this).autocomplete('search');
    }).change(function() {
        populateBuildNumber(this.value);
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
            collision: 'flip',
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
                    collision: 'flip',
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
