var REGEXES = {
    beta: /^\d+\.[\d.]+b\d+(build\d+)?$/, // Examples: 32.0b2, 38.0.5b2, 32.0b10 or 32.0b10build1
    release: /^(\d+\.)+\d$/,        // Examples: 31.0 or 32.0.1
    esr: /^.*\desr.*$/,    // Examples: 31.0esr or 31.1.0esr
    thunderbird: /^(\d+)\.[\d.]*\d$/,
    majorNumber: /^(\d+)\..+/,
    minorNumber: /^\d+\.(\d+).*/,
    patchNumber: /^\d+\.\d+\.(\d+).*/,
    betaNumber: /^.*\db(\d+).*/,
    buildNumber: /^.*build(\d+)$/,
};

function Release(string) {
    ['majorNumber', 'minorNumber'].forEach(function(field) {
        this._assignMandatoryField(field, string);
    }, this);

    ['patchNumber', 'betaNumber', 'buildNumber'].forEach(function(field) {
        this._assignFieldIfItExists(field, string);
    }, this);

    this.isEsr = string.match(REGEXES.esr) !== null;

    if (this.isEsr && this.isBeta) {
        throw new Error('Release cannot be an ESR and a Beta at the same time');
    }
}

function _compareNumbers(first, second) {
    // first and second may be both undefined
    if (first === second) {
        return 0;
    }

    var result = first - second;
    if (isNaN(result)) {
        throw new Error('One of the paramater is not a Number');
    }
    return result;
}

Release.prototype = {
    _assignMandatoryField: function(field, string) {
        var matchResults = string.match(REGEXES[field]);
        if (matchResults === null) {
            throw new MissingFieldError(field);
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

    get isBeta() {
        return this.betaNumber !== undefined;
    },

    get isProductionRelease() {
        return !(this.isBeta || this.isEsr);
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
        ['isBeta', 'isEsr', 'isProductionRelease'].forEach(function(field) {
            // In the 38 cycle, we built the 38 beta version from the
            // mozilla-release branch. We don't want beta partials for a release
            // This is confusing ship-it (and us)
            if (this[field] !== otherRelease[field]) {
                throw new NotComparableError(field);
            }
        }, this);

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

    toString: function() {
        var semvers = [this.majorNumber, this.minorNumber];
        if (this.patchNumber !== undefined) {
            semvers.push(this.patchNumber);
        }
        var string = semvers.join('.');

        if (this.isEsr) {
            string += 'esr';
        }

        if (this.isBeta) {
            string += 'b' + this.betaNumber;
        }

        if (this.buildNumber !== undefined) {
            string += 'build' + this.buildNumber;
        }

        return string;
    }
};
