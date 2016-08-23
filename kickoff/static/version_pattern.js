// Warning: This file is also interpreted by the Python code. You may need to update Python
// tests as well.
//
// Second warning: Changing the bracket orders will require to update INDEXES and
// TYPE_INDEXES in static/model/release.js
var VALID_VERSION_PATTERN_STRING = '^(\\d+)\\.(' + // Major version number
    '(0)(a1|a2|b(\\d+)|esr)?' +   // 2-digit-versions (like 46.0, 46.0b1, 46.0esr)
    '|(' +    // Here begins the 3-digit-versions.
        '([1-9]\\d*)\\.(\\d+)|(\\d+)\\.([1-9]\\d*)' +  // 46.0.0 is not correct
    ')(esr)?' + // Neither is 46.2.0b1
')(build(\\d+))?$';  // See more examples of (in)valid versions in the tests
