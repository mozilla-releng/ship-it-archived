var VALID_VERSIONS = [
    { string: '32.0a1', type: 'nightly' },
    { string: '32.0a2', type: 'devedition' },
    { string: '32.0b2', type: 'beta' },
    { string: '32.0b10', type: 'beta' },
    { string: '32.0', type: 'release' },
    { string: '32.0.1', type: 'release' },
    { string: '32.0esr', type: 'esr' },
    { string: '32.0.1esr', type: 'esr' },
];

function assertVersionHasType(assert, version, hasType, expectedType) {
    var expectedCondition = version.type === expectedType;

    var message = version.string + ' is ';
    if (expectedCondition) {
        message += 'NOT ';
    }
    message += 'detected as ' + expectedType;

    assert.equal(hasType, expectedCondition, message);
}


[isBeta, isESR, isRelease].forEach(function(functionToTest) {
  QUnit.test(functionToTest.name, function(assert) {
      VALID_VERSIONS.forEach(function(version) {
          var expectedType = functionToTest.name.substring('is'.length).toLowerCase();
          var hasType = functionToTest(version.string);
          assertVersionHasType(assert, version, hasType, expectedType)
      });
  });
});

///////////////////////////////////////////////////

QUnit.test( "isTBRelease", function( assert ) {
assert.ok( isTBRelease("32.0b2") == false);
assert.ok( isTBRelease("32.2"));
assert.ok( isTBRelease("32.2.3"));
assert.ok( isTBRelease("32.b2") == false);
assert.ok( isTBRelease("32.0.4b2") == false);
assert.ok( isTBRelease("32.0a2") == false);
assert.ok( isTBRelease("32.0.1esr") == false);
assert.ok( isTBRelease("32.0esr") == false);
});

///////////////////////////////////////////////////

QUnit.test( "isTB", function( assert ) {
assert.ok( isTB("thunderbird"));
assert.ok( isTB("firefox") == false);
assert.ok( isTB("foo") == false);
assert.ok( isTB("fennec") == false);
});


///////////////////////////////////////////////////

QUnit.test( "getBaseRepository", function( assert ) {
assert.strictEqual( getBaseRepository("thunderbird"), "releases/comm-");
assert.strictEqual( getBaseRepository("firefox"), "releases/mozilla-");
});


///////////////////////////////////////////////////

QUnit.test( "guessBranchFromVersion", function( assert ) {
assert.strictEqual( guessBranchFromVersion("thunderbird", ""), "");
assert.strictEqual( guessBranchFromVersion("firefox", ""), "");
assert.strictEqual( guessBranchFromVersion("fennec", ""), "");
assert.strictEqual( guessBranchFromVersion("thunderbird", "31.0.1"), "releases/comm-esr31");
assert.strictEqual( guessBranchFromVersion("firefox", "32.0b2"), "releases/mozilla-beta");
assert.strictEqual( guessBranchFromVersion("fennec", "32.0b2"), "releases/mozilla-beta");
assert.strictEqual( guessBranchFromVersion("firefox", "31.0esr"), "releases/mozilla-esr31");
//assert.strictEqual( guessBranchFromVersion("thunderbird", "31.0.1"), "releases/mozilla-esr31");
assert.strictEqual( guessBranchFromVersion("thunderbird", "31.0.1"), "releases/comm-esr31");
assert.strictEqual( guessBranchFromVersion("firefox", "31.0.1esr"), "releases/mozilla-esr31");
});



///////////////////////////////////////////////////

QUnit.test( "craftLastReleasesAsPartials", function( assert ) {
    name="firefox";
    base = getBaseRepository(name);
    previousBuilds = {
        "releases/mozilla-beta": [
            "31.0b2build2", "30.0b9build2", "29.0b10build2", "25.0b5build2",
            // Test data for human sort. See bug 1289627.
            "48.0b1build2","47.0b9build1","47.0b8build1", "48.0b9build1", "48.0b7build1", "48.0b6build1"
        ],
        "releases/mozilla-release": ["33.0.1build2", "32.0.1build2",  "28.0build2", "27.0build2"],
        "releases/mozilla-esr31": ["31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "24.3.0esrbuild1" ]
    };

    previousReleases = previousBuilds[base + 'release'].sort().reverse();
    assert.deepEqual( craftLastReleasesAsPartials("35.0", previousReleases, 1), ["33.0.1build2"]);

    previousReleases = previousBuilds[base + 'beta'].sort().reverse();
    assert.deepEqual( craftLastReleasesAsPartials("35.0b2", previousReleases, 1), ["31.0b2build2"]);
    assert.deepEqual( craftLastReleasesAsPartials("48.0b10", previousReleases, 3), ["48.0b9build1", "48.0b7build1", "48.0b6build1"]);

    previousReleases = previousBuilds[base + 'esr31'].sort().reverse();
    assert.deepEqual( craftLastReleasesAsPartials("38.0esr", previousReleases, 1), ["31.1.0esrbuild1"]);
});


///////////////////////////////////////////////////

QUnit.test( "stripBuildNumber", function( assert ) {

    assert.strictEqual( stripBuildNumber("35.0build2"), "35.0");
    assert.strictEqual( stripBuildNumber("36.0build1"), "36.0");
    assert.strictEqual( stripBuildNumber("36.0"), "36.0");

});


///////////////////////////////////////////////////

QUnit.test( "getVersionWithBuildNumber", function( assert ) {

    beta=["31.0b2build3", "30.0b9build2", "29.0b10build2", "25.0b5build2", ];
    release=["33.0.1build2", "33.0build1", "32.0.1build2",  "28.0build2", "27.0build2"];
    esr=["31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "24.3.0esrbuild1"];
    tb_esr=["45.2.0build1", "45.1.1build2", "45.1.0build3"];

    assert.strictEqual(getVersionWithBuildNumber("31.0b2", beta), "31.0b2build3");
    assert.strictEqual(getVersionWithBuildNumber("33.0.1", release), "33.0.1build2");
    assert.strictEqual(getVersionWithBuildNumber("33.0", release), "33.0build1");
    assert.strictEqual(getVersionWithBuildNumber("27.0", release), "27.0build2");
    assert.strictEqual(getVersionWithBuildNumber("31.1.0esr", esr), "31.1.0esrbuild1");
    assert.strictEqual(getVersionWithBuildNumber("69.1.0esr", esr), undefined)
    assert.strictEqual(getVersionWithBuildNumber("45.1.1", tb_esr), "45.1.1build2");

});


///////////////////////////////////////////////////

QUnit.test( "populatePartial", function( assert ) {

allPartialJ='{"release": [{"version": "32.0.1", "ADI": 949}, {"version": "31.0", "ADI": 821}, {"version": "30.0.5", "ADI": 661}, {"version": "29.0", "ADI": 438}, {"version": "28.0", "ADI": 256}],' +
            ' "beta": [{"version": "31.0b2", "ADI": 951}, {"version": "31.0b3", "ADI": 879}, {"version": "30.0b9", "ADI": 776}, {"version": "30.0b2", "ADI": 655}, {"version": "29.0b10", "ADI": 273}],' +
            ' "esr": [{"version": "31.1.0esr", "ADI": 833}, {"version": "29.4.0esr", "ADI": 763}, {"version": "24.3.0esr", "ADI": 624}, {"version": "29.0esr", "ADI": 558}, {"version": "31.3.0esr", "ADI": 368}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-beta": ["31.0b3build4", "31.0b2build2", "30.0b9build2", "30.0b2build1", "29.0b10build2", "25.0b5build2"],
                  "releases/mozilla-release": ["33.0.1build2", "32.0.1build2",  "31.1.0build2", "31.0build2", "30.0.5build7", "29.0build2", "28.0build2", "27.0build2"],
                  "releases/mozilla-esr31": ["31.3.0esrbuild1", "31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "29.0esrbuild1", "24.3.0esrbuild1"]};

partialElement = $('#partials');
partialElement.hide();
// Stable (will use partialFXRelease)
var result = populatePartial("firefox", "33.0.2", previousBuilds, partialElement);
assert.ok( result );
// 33.0.1 has 0 as ADI but this is ok
// Take the two next partials with the most ADI
assert.strictEqual($('#partials').val(), "33.0.1build2,32.0.1build2,31.0build2")

// Beta (will use partialFXBeta)
partialElement = $('#partials');
var result = populatePartial("firefox", "33.0b2", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.0b3build4,31.0b2build2,30.0b9build2");

partialElement = $('#partials');
var result = populatePartial("firefox", "24.2.0esr", previousBuilds, partialElement);
assert.ok( !result );
// Empty on purpose. 31.0.2esr is less recent
assert.strictEqual($('#partials').val(), "");

partialElement = $('#partials');
var result = populatePartial("firefox", "31.2.0esr", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.1.0esrbuild1");

// Thunderbird
previousBuilds = {"releases/comm-esr31": ["31.0build1", "24.4.0build1", "24.3.0build1", "24.1.0build1"]},

partialElement = $('#partials');
var result = populatePartial("thunderbird", "31.2.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.0build1,24.4.0build1,24.3.0build1");


// Test case to make sure we will take important ADI in a previous release
allPartialJ='{"release": [{"version": "36.0.4", "ADI": 5000}, {"version": "36.0.3", "ADI": 5000},  {"version": "35.0", "ADI": 3000}, {"version": "36.0", "ADI": 500}, {"version": "36.0.2", "ADI": 300}]}';
allPartial=JSON.parse(allPartialJ);


previousBuilds = {"releases/mozilla-release": ["36.0.4build2", "36.0.3build2",  "36.0.2build2", "36.0build2", "35.0build2"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "37.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "36.0.4build2,36.0.3build2,35.0build2");

// Test the case we had during the 38 cycle (beta built from m-r)
allPartialJ='{"release": [{"version": "38.0.3", "ADI": 5000}, {"version": "35.0", "ADI": 3000}, {"version": "36.0", "ADI": 500}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-release": ["38.0.3build2", "38.0b6build2",  "36.0build2", "35.0build2"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "39.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "38.0.3build2,35.0build2,36.0build2");

// Test the case we had during the 38 cycle (ship-it didn't understand that 38.0.5b3 was a beta)
allPartialJ='{"release": [{"version": "38.0.3", "ADI": 5000}, {"version": "35.0", "ADI": 3000}, {"version": "36.0", "ADI": 500}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-release": ["38.0b3build2", "38.0.3build2", "38.0b6build2",  "36.0build2", "35.0build2"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "39.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "38.0.3build2,35.0build2,36.0build2");

// Test case for release RC builds, where we include the last beta in the list of partials
allPartialJ='{"release": [{"version": "48.0.1", "ADI": 5000}, {"version": "48.0", "ADI": 1000}, {"version": "47.0.1", "ADI": 750}, {"version": "47.0", "ADI": 500}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-release": ["48.0.1build1", "48.0build2", "47.0.1build2",  "47.0build3"],
                  "releases/mozilla-beta":    ["49.0b10build1", "49.0b9build1", "49.0b8build2", "49.0b7build1"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "49.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "49.0b10build1,48.0.1build1,48.0build2");

// Test case for early beta builds for Firefox, where we include the last RC in the list of partials
allPartialJ='{"release": [{"version": "48.0.1", "ADI": 5000}, {"version": "48.0", "ADI": 1000}, {"version": "47.0.1", "ADI": 750}, {"version": "47.0", "ADI": 500}],' +
            ' "beta": [{"version": "48.0.0b10", "ADI": 951}, {"version": "48.0b9", "ADI": 879}, {"version": "48.0b8", "ADI": 776}, {"version": "48.0b7"}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-release": ["48.0.1build1", "48.0build2", "47.0.1build2",  "47.0build3"],
                  "releases/mozilla-beta":    ["48.0build2", "48.0b10build1", "48.0b9build1", "48.0b8build2", "48.0b7build1"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "49.0b1", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "48.0build2,48.0b10build1,48.0b9build1");

// Verify only 1 ESR build remains. In bug 1415268, we realized too many partials were added.
// This was caused by allPartialJ are ordered by number of ADIs (instead by release number).
allPartialJ='{"esr": [{"version": "52.4.0esr", "ADI": 5000}, {"version": "52.3.0esr", "ADI": 4000}, {"version": "52.4.1esr", "ADI": 3000}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-esr52": ["52.4.1esrbuild1", "52.4.0esrbuild2", "52.3.0esrbuild2"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "52.5.0esr", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "52.4.1esrbuild1");

});

QUnit.test('getElmoUrl()', function(assert) {
    var data = [{
        product: 'firefox', majorVersion: 32,
        expectedUrl: 'https://l10n.mozilla.org/shipping/l10n-changesets?av=fx32',
    }, {
        product: 'thunderbird', majorVersion: 33,
        expectedUrl: 'https://l10n.mozilla.org/shipping/l10n-changesets?av=tb33',
    }, {
        product: 'fennec', majorVersion: 32.0,
        expectedUrl: 'https://l10n.mozilla.org/shipping/json-changesets?av=fennec32&platforms=android' +
            '&multi_android-multilocale_repo=releases/mozilla-beta&multi_android-multilocale_rev=default' +
            '&multi_android-multilocale_path=mobile/android/locales/maemo-locales',
    }];

    data.forEach(function(piece) {
        assert.equal(
            getElmoUrl(piece.product, piece.majorVersion),
            piece.expectedUrl
        );
    });
});

QUnit.test('_getPreviousBuildL10nUrl()', function(assert) {
    var data = [{
        product: 'firefox', version: new Version('32.0build1'),
        // We get file:/// because tests run under grunt-qunit
        expectedUrl: 'file:///releases/firefox-32.0-build1/l10n',
    }, {
        product: 'thunderbird', version: new Version('33.0build2'),
        expectedUrl: 'file:///releases/thunderbird-33.0-build2/l10n',
    }, {
        product: 'fennec', version: new Version('32.0b1build3'),
        expectedUrl: 'file:///releases/fennec-32.0b1-build3/l10n'
    }];

    data.forEach(function(piece) {
        assert.equal(
            _getPreviousBuildL10nUrl(piece.product, piece.version, piece.previousBuildNumber),
            piece.expectedUrl
        );
    });
});

QUnit.test('_getUrlAndMessages()', function(assert) {
    var data = [{
        product: 'firefox', version: '32.0', buildNumber: 1, revision: 'unused',
        expectedUrl: 'https://l10n.mozilla.org/shipping/l10n-changesets?av=fx32',
    }, {
        product: 'fennec', version: '32.0', buildNumber: 1, revision: 'unused',
        expectedUrl: 'https://l10n.mozilla.org/shipping/json-changesets?av=fennec32&platforms=android' +
            '&multi_android-multilocale_repo=releases/mozilla-beta' +
            '&multi_android-multilocale_rev=default' +
            '&multi_android-multilocale_path=mobile/android/locales/maemo-locales',
    }, {
        // We get file:/// because tests run under grunt-qunit
        product: 'thunderbird', version: '33.0', buildNumber: 2, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/thunderbird-33.0-build1/l10n',
    }, {
        product: 'firefox', version: '44.0.1', buildNumber: 1, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-44.0-build1/l10n',
    }, {
        product: 'firefox', version: '45.6.0esr', buildNumber: 2, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-45.6.0esr-build1/l10n',
    }, {
        product: 'firefox', version: '45.6.1esr', buildNumber: 1, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-45.6.0esr-build1/l10n',
    }, {
        product: 'firefox', version: '45.6.1esr', buildNumber: 2, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-45.6.1esr-build1/l10n',
    }, {
        product: 'firefox', version: '57.0.1', buildNumber: 1, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-57.0-build1/l10n',
    }, {
        product: 'firefox', version: '57.0.2', buildNumber: 1, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-57.0.1-build1/l10n',
    }, {
        product: 'firefox', version: '45.6.1esr', buildNumber: 2, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-45.6.1esr-build1/l10n',
    }, {
        product: 'fennec', version: '32.0b1', buildNumber: 3, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/fennec-32.0b1-build2/l10n',
    }, {
        // Starting Firefox/Devedition/Fennec 59, l10nChangesets are fetched in-tree (not Thunderbird, though)
        product: 'firefox', version: '59.0b1', buildNumber: 1, branchName: 'mozilla-beta', revision: 'abcdef123456',
        expectedUrl: 'https://hg.mozilla.org/mozilla-beta/raw-file/abcdef123456/browser/locales/l10n-changesets.json',
    }, {
        product: 'devedition', version: '59.0b1', buildNumber: 1, branchName: 'mozilla-beta', revision: 'abcdef123456',
        expectedUrl: 'https://hg.mozilla.org/mozilla-beta/raw-file/abcdef123456/browser/locales/l10n-changesets.json',
    }, {
        product: 'fennec', version: '59.0', buildNumber: 1, branchName: 'mozilla-release', revision: '123456abcdef',
        expectedUrl: 'https://hg.mozilla.org/mozilla-release/raw-file/123456abcdef/mobile/locales/l10n-changesets.json',
    }, {
        product: 'thunderbird', version: '59.0', buildNumber: 1, branchName: 'unused', revision: 'unused',
        expectedUrl: 'https://l10n.mozilla.org/shipping/l10n-changesets?av=tb59',
    }, {
        // Build 2 is still copied from previous build
        product: 'firefox', version: '59.0b1', buildNumber: 2, branchName: 'unused', revision: 'unused',
        expectedUrl: 'file:///releases/firefox-59.0b1-build1/l10n',
    }];

    data.forEach(function(piece) {
        assert.equal(
            _getUrlAndMessages(piece.product, piece.version, piece.buildNumber, piece.branchName, piece.revision).url,
            piece.expectedUrl
        );
    });
});

QUnit.test('getTreeStatusUrl()', function(assert) {
    var data = [{
        branch: 'releases/mozilla-release',
        expectedUrl: 'https://treestatus.mozilla.org/mozilla-release?format=json',
    }, {
        branch: 'releases/mozilla-beta',
        expectedUrl: 'https://treestatus.mozilla.org/mozilla-beta?format=json',
    }, {
        branch: 'releases/comm-beta',
        expectedUrl: 'https://treestatus.mozilla.org/comm-beta-thunderbird?format=json',
    }, {
        branch: 'releases/comm-esr45',
        expectedUrl: 'https://treestatus.mozilla.org/comm-esr45-thunderbird?format=json',
    }];

    data.forEach(function(piece) {
        assert.equal(
            getTreeStatusUrl(piece.branch, piece.version),
            piece.expectedUrl
        );
    });
});


QUnit.test('getJsonPushesUrl()', function(assert) {
    var data = [{
        branch: 'releases/mozilla-release',
        expectedUrl: 'https://hg.mozilla.org/releases/mozilla-release/json-pushes',
    }, {
        branch: 'releases/mozilla-beta',
        expectedUrl: 'https://hg.mozilla.org/releases/mozilla-beta/json-pushes',
    }, {
        branch: 'releases/comm-beta',
        expectedUrl: 'https://hg.mozilla.org/releases/comm-beta/json-pushes',
    }, {
        branch: 'releases/comm-esr45',
        expectedUrl: 'https://hg.mozilla.org/releases/comm-esr45/json-pushes',
    }];

    data.forEach(function(piece) {
        assert.equal(
            getJsonPushesUrl(piece.branch),
            piece.expectedUrl
        );
    });
});

QUnit.test('pluckLatestRevision()', function(assert) {
    jsonPush = {
        "6527": {
            "changesets": ["00f11e7650b184162dbedf9c82a7917b5c07d216", "1ad4ab26875c6512b577f8f6974260fcd76d35b6", "79247eb8ce1f6c5e4444c196983cf7630fa62e9c", "d69e6eb5d19f81e22ddd026857e2b5b7b57d37b5"],
            "date": 1477014593,
            "user": "r@g.c"
        },
        "6528": {
            "changesets": ["328aacd63a389e49956cc34b3be052ffd5f5b519", "0f6ce21169761fde4d0d9058984b1ba3c651e6b5"],
            "date": 1477082000,
            "user": "ffxbld"
        },
        "6529": {
            "changesets": ["41f4ad2acadfef63851abed019bad9b91923b8fc", "f8422ce3d9c6743ef467c1e3394fb83762298a8c", "29a171c7f26dcff9326ffd950e5446ee1f9d0d7b", "fac7c4b729ccd735faa0c4434ae7eede3be95dd6"],
            "date": 1477246215,
            "user": "r@g.c"
        }
    };

    assert.equal(pluckLatestRevision(jsonPush), 'fac7c4b729ccd735faa0c4434ae7eede3be95dd6');
});


QUnit.module('model/Version');

QUnit.test('constructor must throw errors when release has more than one type', function(assert) {
    var invalidVersions = [
        { string: '32', error: InvalidVersionError },
        { string: '32.b2', error: InvalidVersionError },
        { string: '.1', error: InvalidVersionError  },
        { string: '32.2', error: InvalidVersionError },
        { string: '32.02', error: InvalidVersionError },

        { string: '32.0a1a2', error: InvalidVersionError },
        { string: '32.0a1b2', error: InvalidVersionError },
        { string: '32.0b2esr', error: InvalidVersionError },
        { string: '32.0esrb2', error: InvalidVersionError },
    ];

    invalidVersions.forEach(function(invalidVersion) {
        assert.throws(
            function() {
                new Version(invalidVersion.string);
            },
            invalidVersion.error,
            invalidVersion.string + ' did not throw ' + invalidVersion.error.name
        );
    });
});

QUnit.test('is*()', function(assert) {
    VALID_VERSIONS.forEach(function(versionData) {
        var release = new Version(versionData.string);

        Version.POSSIBLE_TYPES.forEach(function(field) {
            var expectedType = field.substring('is'.length).toLowerCase();
            var hasType = release[field];

            assertVersionHasType(assert, versionData, hasType, expectedType)
        });
    });
});

function assertIsNotStrictlyPreviousTo(assert, candidateA, candidateB) {
    assert.ok(
        !candidateA.isStrictlyPreviousTo(candidateB),
        candidateA + ' IS declared as previous to ' + candidateB
    );
}

QUnit.test('isStrictlyPreviousTo() must compare different version numbers', function(assert) {
    var data = [
        { previous: '32.0', next: '33.0' },
        { previous: '32.0', next: '32.1.0' },
        { previous: '32.0', next: '32.0.1' },
        { previous: '32.0build1', next: '32.0build2' },

        { previous: '32.0.1', next: '33.0' },
        { previous: '32.0.1', next: '32.1.0' },
        { previous: '32.0.1', next: '32.0.2' },
        { previous: '32.0.1build1', next: '32.0.1build2' },

        { previous: '32.1.0', next: '33.0' },
        { previous: '32.1.0', next: '32.2.0' },
        { previous: '32.1.0', next: '32.1.1' },
        { previous: '32.1.0build1', next: '32.1.0build2' },

        { previous: '32.0b10', next: '32.0'},
        { previous: '32.0', next: '33.0b1'},

        { previous: '32.0b1', next: '33.0b1' },
        { previous: '32.0b1', next: '32.0b2' },
        { previous: '32.0b1build1', next: '32.0b1build2' },

        { previous: '2.0', next: '10.0' },
        { previous: '10.2.0', next: '10.10.0' },
        { previous: '10.0.2', next: '10.0.10' },
        { previous: '10.10.1', next: '10.10.10' },
        { previous: '10.0build2', next: '10.0build10' },
        { previous: '10.0b2', next: '10.0b10' },
    ];

    data = data.map(function(couple) {
        return {
            previous: new Version(couple.previous),
            next: new Version(couple.next),
        };
    });

    data.forEach(function(couple) {
        assert.ok(
            couple.previous.isStrictlyPreviousTo(couple.next),
            couple.previous + ' is NOT declared as previous to ' + couple.next
        );
        assertIsNotStrictlyPreviousTo(assert, couple.next, couple.previous);
    });
});

QUnit.test('isStrictlyPreviousTo() must compare identical version numbers', function(assert) {
    var baseCandidate = new Version('32.0');
    var equalCandidates = ['32.0', '32.0build1'];
    equalCandidates = equalCandidates.map(function(candidate) {
        return new Version(candidate);
    });

    equalCandidates.forEach(function(candidate) {
        assertIsNotStrictlyPreviousTo(assert, baseCandidate, candidate);
    });
});

QUnit.test('isStrictlyPreviousTo() must throw errors when not comparable', function(assert) {
    var data = [
        { a: '32.0', b: '32.0a1' },
        { a: '32.0', b: '32.0a2' },
        // comparing '32.0' to '32.0b1' is permitted
        { a: '32.0', b: '32.0esr' },

        { a: '32.0a1', b: '32.0a2' },
        { a: '32.0a1', b: '32.0b1' },
        { a: '32.0a1', b: '32.0esr' },

        { a: '32.0a2', b: '32.0b1' },
        { a: '32.0a2', b: '32.0esr' },

        { a: '32.0b1', b: '32.0esr' },
    ];

    data = data.map(function(couple) {
        return {
            a: new Version(couple.a),
            b: new Version(couple.b),
        };
    });

    data.forEach(function(couple) {
        assert.throws(
            function() {
                couple.a.isStrictlyPreviousTo(couple.b);
            },
            NotComparableError,
            couple.a + ' can be compared to ' + couple.b
        );
    });
});

QUnit.test('toString()', function(assert) {
    var data = {
        '32.0': ['32.0', '032.0'],
        '32.0.1': ['32.0.1'],
        '32.0build1': ['32.0build1', '32.0build01'],
        '32.0a1': ['32.0a1'],
        '32.0a2': ['32.0a2'],
        '32.0b1': ['32.0b1', '32.0b01'],
        '32.0esr': ['32.0esr'],
        '32.0.1esr': ['32.0.1esr'],
        '32.1.0esr': ['32.1.0esr'],
    }

    for (var expectedString in data) {
        var candidates = data[expectedString];
        candidates = candidates.map(function(candidate) {
            return new Version(candidate).toString();
        })

        candidates.forEach(function(candidate) {
            assert.equal(candidate, expectedString);
        })
    }
});

QUnit.module('datetime');

QUnit.test('convertMinutesToUtcString()', function(assert) {
    assert.equal(convertMinutesToUtcString(0), '00:00 UTC');
    assert.equal(convertMinutesToUtcString(721), '12:01 UTC');
    assert.equal(convertMinutesToUtcString(1439), '23:59 UTC');
});

QUnit.test('convertUtcStringToNumberOfMinutes()', function(assert) {
    assert.equal(convertUtcStringToNumberOfMinutes('00:00 UTC'), 0);
    assert.equal(convertUtcStringToNumberOfMinutes('12:01 UTC'), 721);
    assert.equal(convertUtcStringToNumberOfMinutes('23:59 UTC'), 1439);
});

QUnit.test('pad()', function(assert) {
    assert.equal(pad(0), '00');
    assert.equal(pad(0, 2), '00');
    assert.equal(pad(0, 2, 0), '00');
    assert.equal(pad(1), '01');
    assert.equal(pad(10), '10');
    assert.equal(pad(123), '123');
});
