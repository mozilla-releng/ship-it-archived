function _isTreeForThunderbird(treeName) {
    return treeName.indexOf('comm') > -1;
}

function getTreeStatusUrl(branchName) {
    var treeName = branchName.split('/')[1];
    if (_isTreeForThunderbird(treeName)) {
        treeName += '-thunderbird';
    }

    return CONFIG.baseUrls.treestatus + treeName + '?format=json';
}

function fetchTreeStatus(branchElement, newerBranchName) {
    var branchName = newerBranchName ? newerBranchName : branchElement.val();

    var warningElement = branchElement.siblings('.help').find('.warning');
    warningElement.text('');

    $.ajax({
        url: getTreeStatusUrl(branchName),
    }).done(function(results) {
        var status = results.status;
        if (status !== 'open' && status !== 'approval required') {
            var message = 'Warning: ' + branchName + ' has status "' + status + '". Reason: ' + results.reason;
            warningElement.text(message);
        }
    }).fail(function() {
        console.error('Could not fetch status of tree "' + branchName + '"');
    });
}

$(document).ready(function() {
    SUPPORTED_PRODUCTS.forEach(function(productName) {
        var branchElement = $('#' + productName + '-branch');
        if (branchElement.autocomplete) {
            branchElement.autocomplete({
                select: function(_, ui) {
                    var newerBranchName = ui.item.value;
                    if (newerBranchName) {
                        fetchTreeStatus(branchElement, newerBranchName);
                    }
                }
            }).change(function() {
                fetchTreeStatus(branchElement);
            });
        }
    });
});
