
QUnit.test( "isBeta", function( assert ) {
assert.ok( isBeta("32.0b2"));
assert.ok( isBeta("32.02") == false);
assert.ok( isBeta("32.b2") == false);
assert.ok( isBeta("32.0a2") == false);
assert.ok( isBeta("32.0") == false);
assert.ok( isBeta("32.0.1esr") == false);
});


///////////////////////////////////////////////////

QUnit.test( "isESR", function( assert ) {
assert.ok( isESR("32.0b2") == false);
assert.ok( isESR("32.02") == false);
assert.ok( isESR("32.b2") == false);
assert.ok( isESR("32.0a2") == false);
assert.ok( isESR("32.0.1") == false);
assert.ok( isESR("32.0.1esr"));
assert.ok( isESR("32.0esr"));
});


///////////////////////////////////////////////////

QUnit.test( "isRelease", function( assert ) {
assert.ok( isRelease("32.0b2") == false);
assert.ok( isRelease("32.2"));
assert.ok( isRelease("32.2.3"));
assert.ok( isRelease("32.b2") == false);
assert.ok( isRelease("32.0a2") == false);
assert.ok( isRelease("32.0.1esr") == false);
assert.ok( isRelease("32.0esr") == false);
});


///////////////////////////////////////////////////

QUnit.test( "isTBRelease", function( assert ) {
assert.ok( isTBRelease("32.0b2") == false);
assert.ok( isTBRelease("32.2"));
assert.ok( isTBRelease("32.2.3"));
assert.ok( isTBRelease("32.b2") == false);
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

QUnit.test( "addLastVersionAsPartial", function( assert ) {
    name="firefox";
    base = getBaseRepository(name);
    previousBuilds = {"releases/mozilla-beta": ["31.0b2build2", "30.0b9build2", "29.0b10build2", "25.0b5build2", ],
                      "releases/mozilla-release": ["33.0.1build2", "32.0.1build2",  "28.0build2", "27.0build2"],
                      "releases/mozilla-esr31": ["31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "24.3.0esrbuild1" ]};

    previousReleases = previousBuilds[base + 'release'].sort().reverse();
    assert.strictEqual( addLastVersionAsPartial("35.0", previousReleases, 1), "33.0.1build2,");

    previousReleases = previousBuilds[base + 'beta'].sort().reverse();
    assert.strictEqual( addLastVersionAsPartial("35.0b2", previousReleases, 1), "31.0b2build2,");

    previousReleases = previousBuilds[base + 'esr31'].sort().reverse();
    assert.strictEqual( addLastVersionAsPartial("38.0esr", previousReleases, 1), "31.1.0esrbuild1,");
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
    release=["33.0.1build2", "32.0.1build2",  "28.0build2", "27.0build2"];
    esr=["31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "24.3.0esrbuild1"];

    assert.strictEqual(getVersionWithBuildNumber("31.0b2", beta), "31.0b2build3");
    assert.strictEqual(getVersionWithBuildNumber("33.0.1", release), "33.0.1build2");
    assert.strictEqual(getVersionWithBuildNumber("27.0", release), "27.0build2");
    assert.strictEqual(getVersionWithBuildNumber("31.1.0", esr), "31.1.0esrbuild1");
    assert.strictEqual(getVersionWithBuildNumber("69.1.0", esr), undefined)

});


///////////////////////////////////////////////////

QUnit.test( "populatePartial", function( assert ) {

allPartialJ='{"release": [{"version": "32.0.1", "ADI": 949}, {"version": "31.0", "ADI": 821}, {"version": "30.0.5", "ADI": 661}, {"version": "29.0", "ADI": 438}, {"version": "28.0", "ADI": 256}], "beta": [{"version": "31.0b2", "ADI": 951}, {"version": "31.0b3", "ADI": 879}, {"version": "30.0b9", "ADI": 776}, {"version": "30.0b2", "ADI": 655}, {"version": "29.0b10", "ADI": 273}], "esr": [{"version": "31.1.0", "ADI": 833}, {"version": "29.4.0", "ADI": 763}, {"version": "24.3.0", "ADI": 624}, {"version": "29.0", "ADI": 558}, {"version": "31.3.0", "ADI": 368}]}';
allPartial=JSON.parse(allPartialJ);

previousBuilds = {"releases/mozilla-beta": ["31.0b3build4", "31.0b2build2", "30.0b9build2", "29.0b10build2", "25.0b5build2", "30.0b2build1" ],
                  "releases/mozilla-release": ["33.0.1build2", "31.1.0build2", "32.0.1build2", "31.0build2", "28.0build2", "27.0build2", "29.0build2", "30.0.5build7"],
                  "releases/mozilla-esr31": ["31.1.0esrbuild1", "29.4.0esrbuild1", "29.2.0esrbuild1", "24.3.0esrbuild1", "29.0esrbuild1", "31.3.0esrbuild1" ]};

partialElement = $('#partials');
partialElement.hide();
// Stable (will use partialFXRelease)
var result = populatePartial("firefox", "33.2", previousBuilds, partialElement);
assert.ok( result );
// 33.0.1 has 0 as ADI but this is ok
// Take the two next partials with the most ADI
assert.strictEqual($('#partials').val(), "33.0.1build2,32.0.1build2,31.0build2,30.0.5build7")

// Beta (will use partialFXBeta)
partialElement = $('#partials');
var result = populatePartial("firefox", "33.2b2", previousBuilds, partialElement);
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
assert.strictEqual($('#partials').val(), "31.1.0esrbuild1,29.4.0esrbuild1,24.3.0esrbuild1,29.0esrbuild1");

// Thunderbird
previousBuilds = {"releases/comm-esr31": ["31.0build1", "24.1.0build1", "24.3.0build1", "24.4.0build1"]},

partialElement = $('#partials');
var result = populatePartial("thunderbird", "31.2.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.0build1,24.4.0build1,24.3.0build1");


// Test case to make sure we will take important ADI in a previous release
allPartialJ='{"release": [{"version": "36.0.4", "ADI": 5000}, {"version": "36.0.3", "ADI": 5000},  {"version": "35.0", "ADI": 3000}, {"version": "36.0", "ADI": 500}]}';
allPartial=JSON.parse(allPartialJ);


previousBuilds = {"releases/mozilla-release": ["36.0.4build2", "36.0.3build2",  "36.0build2", "35.0build2"]}

partialElement = $('#partials');
var result = populatePartial("firefox", "37.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "36.0.4build2,36.0.3build2,35.0build2,");

});
