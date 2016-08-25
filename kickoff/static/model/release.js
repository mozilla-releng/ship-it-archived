// Please also update VALID_VERSION_PATTERN in forms.py
// Changing the bracket orders may require to update INDEXES and TYPE_INDEXES
// TODO: Read the pattern from a centralized file
var VALID_VERSION_PATTERN_STRING  = '^(\\d+)\\.(' + // Major version number
    '(0)(a1|a2|b(\\d+)|esr)?' +   // 2-digit-versions (like 46.0, 46.0b1, 46.0esr)
    '|(' +    // Here begins the 3-digit-versions.
        '([1-9]\\d*)\\.(\\d+)|(\\d+)\\.([1-9]\\d*)' +  // 46.0.0 is not correct
    ')(esr)?' + // Neither is 46.2.0b1
')(build(\\d+))?$';  // See more examples of (in)valid versions in the tests

var VALID_VERSION_PATTERN = new RegExp(VALID_VERSION_PATTERN_STRING);

var INDEXES = {
    majorNumber: [1],
    minorNumber: [3, 7, 9],
    patchNumber: [8, 10],
    betaNumber: [5],
    buildNumber: [13],
};

var TYPE_INDEXES = {
    nightly: {keyword: 'a1', indexes: [4]},
    devEdition: {keyword: 'a2', indexes: [4]},
    esr: {keyword: 'esr', indexes: [4, 11]},
};

var REGEXES = {
    beta: /^\d+\.[\d.]+b\d+(build\d+)?$/, // Examples: 32.0b2, 38.0.5b2, 32.0b10 or 32.0b10build1
    release: /^(\d+\.)+\d+$/,        // Examples: 32.0 or 32.0.1
    esr: /^.*\desr.*$/,    // Examples: 32.0esr or 32.2.0esr
    thunderbird: /^(\d+)\.[\d.]*\d$/,
    majorNumber: /^(\d+)\..+/,
};

function doesRegexMatch(string, regex) {
    return string.match(regex) !== null;
}

function Release(string) {
    var matches = string.match(VALID_VERSION_PATTERN);
    if (matches === null) {
        throw new InvalidVersionError(string);
    }

    ['majorNumber', 'minorNumber'].forEach(function(field) {
        this._assignMandatoryField(field, matches, string);
    }, this);

    ['patchNumber', 'betaNumber', 'buildNumber'].forEach(function(field) {
        this._assignFieldIfItExists(field, matches, string);
    }, this);

    ['nightly', 'devEdition', 'esr'].forEach(function(type) {
        this._assignIsType(type, matches, string);
    }, this);

    this._performSanityCheck();
}

function _getMatchValue(matchPotentialIndexes, field, matches, string) {
    var matchValue;
    for (var i = 0; i < matchPotentialIndexes.length; i++) {
        var matchIndex = matchPotentialIndexes[i];
        var matchValue = matches[matchIndex];
        if (matchValue !== undefined) {
            break;
        }
    }

    if (matchValue === undefined) {
        throw new MissingFieldError(string, field);
    }

    return matchValue;
}

function _compareNumbers(first, second) {
    // first may be undefined when comparing 31.0 with 31.0.1, for instance
    first = first || 0;
    second = second || 0; // Same here with 31.0.1 and 31.0

    return first - second;
}

function _capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

Release.POSSIBLE_TYPES = [
    'isNightly', 'isDevEdition', 'isBeta', 'isEsr', 'isRelease'
];

Release.prototype = {

    _assignMandatoryField: function(field, matches, string) {
        var matchPotentialIndexes = INDEXES[field];
        var matchValue = _getMatchValue(matchPotentialIndexes, field, matches, string);
        this[field] = parseInt(matchValue, 10);
    },

    _assignFieldIfItExists: function(field, string) {
        try {
            this._assignMandatoryField(field, string);
        } catch (err) {
            if (!(err instanceof MissingFieldError)) {
                throw err;
            }
        }
    },

    _assignIsType: function(type, matches, string) {
        var field = 'is' + _capitalizeFirstLetter(type);
        var matchPotentialIndexes = TYPE_INDEXES[type].indexes;
        var matchValue;
        try {
            matchValue = _getMatchValue(matchPotentialIndexes, type, matches, string);
        } catch (err) {
            if (!(err instanceof MissingFieldError)) {
                throw err;
            }
        }
        this[field] = matchValue === TYPE_INDEXES[type].keyword;
    },

    _performSanityCheck: function() {
        var self = this;
        var firstFieldToMatch = '';

        Release.POSSIBLE_TYPES.reduce(function(previousValue, currentField) {
            var currentValue = self[currentField];
            if (currentValue === true) {
                if (previousValue === true) {
                    throw new TooManyTypesError(firstFieldToMatch, currentField);
                }

                firstFieldToMatch = currentField;
            }
            return previousValue || currentValue;
        }, false);
    },

    get isBeta() {
        return this.betaNumber !== undefined;
    },

    get isRelease() {
        return !(this.isNightly || this.isDevEdition || this.isBeta || this.isEsr);
    },

    isStrictlyPreviousTo: function(otherRelease) {
        return this._compare(otherRelease) < 0;
    },

    /**
        Compare this release with another. They must be from the same channel
        @return 0 if equal; < 0 is this preceeds the other; > 0 if the other preceeds this
        @throws Error if they're not from the same channel
    */
    _compare: function(otherRelease) {
        this._checkOtherIsOfSameType(otherRelease);

        var orderedFields = ['majorNumber', 'minorNumber', 'patchNumber', 'betaNumber'];
        for (var i = 0; i < orderedFields.length; i++) {
            var field = orderedFields[i];
            var comparisonResult = _compareNumbers(this[field], otherRelease[field]);

            if (comparisonResult !== 0) {
                return comparisonResult;
            }
        }

        // Build numbers are a special case. We might compare a regular version number
        // (like "32.0b8") versus a release build (as in "32.0b8build1"). As a consequence,
        // we only compare buildNumbers when we both have them.
        if (this.buildNumber && otherRelease.buildNumber) {
            return _compareNumbers(this.buildNumber, otherRelease.buildNumber);
        }

        return 0;
    },

    _checkOtherIsOfSameType: function(otherRelease) {
        Release.POSSIBLE_TYPES.forEach(function(field) {
            // In the 38 cycle, we built the 38 beta version from the
            // mozilla-release branch. We don't want beta partials for a release
            // This is confusing ship-it (and us)
            if (this[field] !== otherRelease[field]) {
                throw new NotComparableError(this, otherRelease, field);
            }
        }, this);
    },

    toString: function() {
        var semvers = [this.majorNumber, this.minorNumber];
        if (this.patchNumber !== undefined) {
            semvers.push(this.patchNumber);
        }
        var string = semvers.join('.');

        if (this.isNightly) {
            string += 'a1';
        }

        if (this.isDevEdition) {
            string += 'a2';
        }

        if (this.isBeta) {
            string += 'b' + this.betaNumber;
        }

        if (this.isEsr) {
            string += 'esr';
        }

        if (this.buildNumber !== undefined) {
            string += 'build' + this.buildNumber;
        }

        return string;
    }
};
