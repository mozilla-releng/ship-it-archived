function MissingFieldError(field) {
    this.name = 'MissingFieldError';
    this.message = 'Release does not contain a ' + field;
    this.stack = (new Error()).stack;
}

MissingFieldError.prototype = Object.create(Error.prototype);
MissingFieldError.prototype.constructor = MissingFieldError;

function NotComparableError(field) {
    this.name = 'NotComparableError';
    this.message = 'Cannot compare these two releases. One verifies "' + field +
    '" but the second one does not';
    this.stack = (new Error()).stack;
}

NotComparableError.prototype = Object.create(Error.prototype);
NotComparableError.prototype.constructor = NotComparableError;
