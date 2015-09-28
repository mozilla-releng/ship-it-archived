function initialSetup() {
    // initialize tabs and accordion.
    // Saving last active element using localStorage
    $('#tabs').tabs({
        activate: function(event, ui) {
         localStorage.setItem('active_tab', $('#tabs')
            .tabs('option', 'active'));
     },
        active: parseInt(localStorage.getItem('active_tab')),
    });

    $('#accordion').accordion({
        heightStyle: 'content',
        change: function(event, ui) {
            localStorage.setItem('active_accordion', $('#accordion')
                .accordion('option', 'active'));
        },
        active: parseInt(localStorage.getItem('active_accordion'))
    });

    // Hide all by default
    $('.textareaDiv').hide();
    // Display or hide the textarea to update the description
    $('.showLinkUpdate').click(function() {
        $('.textareaDiv').hide();
        $('.linkUpdate' + $(this).attr('target')).hide();
        $('#description' + $(this).attr('target')).show();
    });

    // Show the tooltip. Mostly use for the "is security driven" checkbox
    $(document).tooltip();

}

function viewReleases() {
    toLocalDate();
    // initial sorting by SubmittedAt (descending)
    // and then saving user table state using localStorage
    $('#reviewed').dataTable({
        'bJQueryUI': true,
        'aaSorting': [[3, 'desc']],
        'bStateSave': true,
        'fnStateSave': function(oSettings, oData) {
        localStorage.setItem('DataTables_reviewed' + window.location.pathname, JSON.stringify(oData));
    },
        'fnStateLoad': function(oSettings) {
        return JSON.parse(localStorage.getItem('DataTables_reviewed' + window.location.pathname));
    }
    });
    $('#running').dataTable({
        'bJQueryUI': true,
        'aaSorting': [[2, 'desc']],
        'bStateSave': true,
        'fnStateSave': function(oSettings, oData) {
        localStorage.setItem('DataTables_running' + window.location.pathname, JSON.stringify(oData));
    },
        'fnStateLoad': function(oSettings) {
        return JSON.parse(localStorage.getItem('DataTables_running' + window.location.pathname));
    }
    });
}

function toLocalDate() {

    $('.dateDisplay').each(function() {
        dateField = $(this).html();
        if (dateField === 'None') {
            // Field not set in the db, don't show anything
            formateddate = '';
        } else {
            var localdate = new Date(dateField);
            // formatDate does not handle hour/minute
            formateddate = $.datepicker.formatDate('yy/mm/dd', localdate) + '<br />' + localdate.getHours() + ':' + (localdate.getMinutes() < 10 ? '0' : '') + localdate.getMinutes();
        }
        if ($(this).prop('tagName') == 'TD') {
            $(this).empty().append(formateddate);
        } else {
            //this is not a table row: prepend 'Date: '
            $(this).empty().append('Date: ' + formateddate);
        }
    });
};

function escapeExpression(str) {
    return str.replace(/([#;&,_\-\.\+\*\~':"\!\^$\[\]\(\)=>\|])/g, '\\$1');
}

function submittedReleaseButtons(buttonId) {
    var btnId = '#' + escapeExpression(buttonId);
    var otherBtnId = btnId.replace('ready', 'delete');
    if (otherBtnId == btnId) {
        otherBtnId = btnId.replace('delete', 'ready');
    }
    if ($(btnId).is(':checked')) {
        $(otherBtnId).attr('checked', false);
        $(otherBtnId).attr('disabled', true);
    } else {
        $(otherBtnId).attr('disabled', false);
    }
}

function sendAjaxQuery(releaseName, query) {
    csrfToken = $('#csrf_token').val();

    var request = $.ajax({
        url: '/releases/' + releaseName,
        type: 'POST',
        data: query + '&csrf_token=' + csrfToken + '&csrfToken=' + csrfToken ,
    });

    request.done(function() {
        location.reload();
    });

    request.fail(function(jqXHR, textStatus) {
        alert('Error: ' + jqXHR.responseText);
    });

}

function updateShip(releaseName, shipped) {

    if (shipped) {
        status = 'postrelease';
        var d = new Date();
        // Expects '%Y-%m-%d %H:%M:%S'
        shippedAt = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + ' ' + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds();
    } else {
        status = 'Started';
        shippedAt = '';
    }
    query = 'status=' + status + '&shippedAt=' + shippedAt;
    sendAjaxQuery(releaseName, query);

}

function updateDesc(releaseName, id) {
    description = $('textarea#desc' + id).val();
    isSecurityDriven = $('#isSecurityDriven' + id).prop('checked');
    query = 'description=' + description + '&isSecurityDriven=' + isSecurityDriven;
    sendAjaxQuery(releaseName, query);
}
