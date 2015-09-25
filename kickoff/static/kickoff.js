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

function updateShip(e, shipped) {
    csrfToken = $('#csrfToken').val();
    if (shipped) {
        status = 'postrelease';
        var d = new Date();
        // Expects '%Y-%m-%d %H:%M:%S'
        shippedAt = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + ' ' + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds();
    } else {
        status = 'Started';
        shippedAt = '';
    }
    var request = $.ajax({
        url: '/releases/' + e,
        type: 'POST',
        data: 'status=' + status + '&shippedAt=' + shippedAt + '&csrfToken=' + csrfToken,
    });

    request.done(function() {
        location.reload();
    });

    request.fail(function(jqXHR, textStatus) {
        alert('Error: ' + jqXHR.responseText);
    });

}
