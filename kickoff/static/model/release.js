var REGEXES = {
    beta: /^\d+\.[\d.]+b\d+(build\d+)?$/, // Examples: 32.0b2, 38.0.5b2, 32.0b10 or 32.0b10build1
    release: /^(\d+\.)+\d+$/,        // Examples: 31.0 or 32.0.1
    nightly: /^.*\da1.*/,
    devEdition: /^.*\da2.*/,
    esr: /^.*\desr.*$/,    // Examples: 31.0esr or 31.1.0esr
    thunderbird: /^(\d+)\.[\d.]*\d$/,
    majorNumber: /^(\d+)\..+/,
    minorNumber: /^\d+\.(\d+).*/,
    patchNumber: /^\d+\.\d+\.(\d+).*/,
    betaNumber: /^.*\db(\d+).*/,
    buildNumber: /^.*build(\d+)$/,
};

function doesRegexMatch(string, regex) {
    return string.match(regex) !== null;
}

function Release(string) {
    ['majorNumber', 'minorNumber'].forEach(function(field) {
        this._assignMandatoryField(field, string);
    }, this);

    ['patchNumber', 'betaNumber', 'buildNumber'].forEach(function(field) {
        this._assignFieldIfItExists(field, string);
    }, this);

    this.isDevEdition = doesRegexMatch(string, REGEXES.devEdition);
    this.isNightly = doesRegexMatch(string, REGEXES.nightly);
    this.isEsr = doesRegexMatch(string, REGEXES.esr);

    this._performSanityCheck();
}

function _compareNumbers(first, second) {
    // first may be undefined when comparing 31.0 with 31.0.1, for instance
    first = first || 0;
    second = second || 0; // Same here with 31.0.1 and 31.0

    return first - second;
}

Release.POSSIBLE_TYPES = [
    'isNightly', 'isDevEdition', 'isBeta', 'isEsr', 'isRelease'
];

Release.prototype = {

    _assignMandatoryField: function(field, string) {
        var matchResults = string.match(REGEXES[field]);
        if (matchResults === null) {
            throw new MissingFieldError(string, field);
        }
        this[field] = parseInt(matchResults[1]);
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

    _performSanityCheck: function() {
        var firstFieldToMatch = '';

        Release.POSSIBLE_TYPES.reduce(function(previousValue, currentField) {
            var currentValue = this[currentField];
            if (currentValue === true) {
                if (previousValue === true) {
                    throw new Error('Release cannot match "' + firstFieldToMatch +
                        '" and "' + currentField + '"'
                    );
                }

                firstFieldToMatch = currentField;
            }
            return currentValue;
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
