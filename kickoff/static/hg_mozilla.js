function getJsonPushesUrl(branchName) {
    return CONFIG.baseUrls.hgMozilla + branchName + '/json-pushes';
}

function pluckLatestRevision(jsonPushes) {
    var pushIds = Object.keys(jsonPushes);
    pushIds = pushIds.map(function(pushId) { return parseInt(pushId); });
    latestPushId = pushIds.reduce(function(latest, challenger) { return challenger > latest ? challenger : latest; });
    latestRevisions = jsonPushes[latestPushId].changesets;
    return latestRevisions[latestRevisions.length - 1];
}

function populateRevisionWithLatest(productName, branchName) {
    var revisionElement = $('#' + productName + '-mozillaRevision');
    var oldPlaceholder = revisionElement.attr('placeholder');

    revisionElement.attr('placeholder', 'Fetching latest revision');
    revisionElement.prop('disabled', true);

    $.ajax({
        url: getJsonPushesUrl(branchName),
    }).done(function(results) {
        var latestRevision = pluckLatestRevision(results);
        revisionElement.val(latestRevision);
        revisionElement.trigger('change'); // this allows fields like revision to react
    }).fail(function() {
        revisionElement.val('');
        console.error('Could not fetch latest revision for branch "' + branchName + '"');
    }).always(function() {
        revisionElement.prop('disabled', false);
        revisionElement.attr('placeholder', oldPlaceholder);
        revisionElement.blur(); // this deactivates relbranch field, if needed
    });
}

function getInTreeFileUrl(branchName, revision, path) {
    return CONFIG.baseUrls.hgMozilla + branchName + '/raw-file/' + revision + '/' + path;
}
