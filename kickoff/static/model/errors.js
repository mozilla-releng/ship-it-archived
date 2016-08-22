function InvalidVersionError(string) {
    this.name = 'InvalidVersionError';
    this.message = 'Version "' + string + '" does not match the pattern of a valid version';
    this.stack = (new Error()).stack;
}

InvalidVersionError.prototype = Object.create(Error.prototype);
InvalidVersionError.prototype.constructor = InvalidVersionError;

function MissingFieldError(string, field) {
    this.name = 'MissingFieldError';
    this.message = 'Release "' + string + '" does not contain a valid ' + field;
    this.stack = (new Error()).stack;
}

MissingFieldError.prototype = Object.create(Error.prototype);
MissingFieldError.prototype.constructor = MissingFieldError;

function NotComparableError(first, second, field) {
    this.name = 'NotComparableError';
    this.message = 'Cannot compare "' + first + '" and "' + second +
        '". One verifies "' + field + '" but the second one does not.';
    this.stack = (new Error()).stack;
}

NotComparableError.prototype = Object.create(Error.prototype);
NotComparableError.prototype.constructor = NotComparableError;

function TooManyTypesError(firstType, secondType) {
    this.name = 'TooManyTypesError';
    this.message = 'Release cannot match "' + firstType + '" and "' + secondType + '"';
    this.stack = (new Error()).stack;
}

TooManyTypesError.prototype = Object.create(Error.prototype);
TooManyTypesError.prototype.constructor = TooManyTypesError;
