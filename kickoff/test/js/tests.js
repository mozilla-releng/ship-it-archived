
QUnit.test( "isBeta", function( assert ) {
assert.ok( isBeta("32.0b2"));
assert.ok( isBeta("32.02") == false);
assert.ok( isBeta("32.b2") == false);
assert.ok( isBeta("32.0a2") == false);
assert.ok( isBeta("32.0") == false);
assert.ok( isBeta("32.0.1esr") == false);
});


QUnit.test( "isESR", function( assert ) {
assert.ok( isESR("32.0b2") == false);
assert.ok( isESR("32.02") == false);
assert.ok( isESR("32.b2") == false);
assert.ok( isESR("32.0a2") == false);
assert.ok( isESR("32.0.1") == false);
assert.ok( isESR("32.0.1esr"));
assert.ok( isESR("32.0esr"));
});

QUnit.test( "isRelease", function( assert ) {
assert.ok( isRelease("32.0b2") == false);
assert.ok( isRelease("32.2"));
assert.ok( isRelease("32.2.3"));
assert.ok( isRelease("32.b2") == false);
assert.ok( isRelease("32.0a2") == false);
assert.ok( isRelease("32.0.1esr") == false);
assert.ok( isRelease("32.0esr") == false);
});


QUnit.test( "isTBRelease", function( assert ) {
assert.ok( isTBRelease("32.0b2") == false);
assert.ok( isTBRelease("32.2"));
assert.ok( isTBRelease("32.2.3"));
assert.ok( isTBRelease("32.b2") == false);
assert.ok( isTBRelease("32.0a2") == false);
assert.ok( isTBRelease("32.0.1esr") == false);
assert.ok( isTBRelease("32.0esr") == false);
});

QUnit.test( "isTB", function( assert ) {
assert.ok( isTB("thunderbird"));
assert.ok( isTB("firefox") == false);
assert.ok( isTB("foo") == false);
assert.ok( isTB("fennec") == false);
});

QUnit.test( "getBaseRepository", function( assert ) {
assert.strictEqual( getBaseRepository("thunderbird"), "releases/comm-");
assert.strictEqual( getBaseRepository("firefox"), "releases/mozilla-");
});

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

QUnit.test( "populatePartial", function( assert ) {
previousBuilds = {"releases/mozilla-beta": ["26.0b5build2", "25.0b5build2", "27.0b5build2", "28.0b5build2"], "releases/mozilla-release": ["27.0build2", "29.0build2", "31.0build2", "28.0build2"], "releases/mozilla-esr31": ["31.0esrbuild1","31.2.0esrbuild1", "24.0.0esrbuild1", "31.1.0esrbuild1"]},

partialElement = $('#partials');
partialElement.hide();
var result = populatePartial("firefox", "33.2", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.0build2,29.0build2,28.0build2,27.0build2");

partialElement = $('#partials');
var result = populatePartial("firefox", "33.2b2", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "28.0b5build2,27.0b5build2,26.0b5build2");

partialElement = $('#partials');
var result = populatePartial("firefox", "24.2.0esr", previousBuilds, partialElement);
assert.ok( result );
// Empty on purpose. 31.0.2esr is less recent
assert.strictEqual($('#partials').val(), "");

partialElement = $('#partials');
var result = populatePartial("firefox", "31.2.0esr", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.1.0esrbuild1,31.0esrbuild1,24.0.0esrbuild1");

// Thunderbird
previousBuilds = {"releases/comm-esr31": ["31.0build1", "24.1.0build1", "24.3.0build1", "24.4.0build1"]},

partialElement = $('#partials');
var result = populatePartial("thunderbird", "31.2.0", previousBuilds, partialElement);
assert.ok( result );
assert.strictEqual($('#partials').val(), "31.0build1,24.4.0build1,24.3.0build1,24.1.0build1");

});
