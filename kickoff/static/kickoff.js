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
    $('table').on('click', 'tbody tr td div .showLinkUpdate', function() {
        $('.textareaDiv').hide();
        $('.linkUpdate' + $(this).attr('target')).hide();
        $('#description' + $(this).attr('target')).show();
    });

    // Show the tooltip. Mostly use for the "is security driven" checkbox
    $(document).tooltip();

}

function viewReleases() {
    var submittedAtIndexColumn = 5;
    var descriptionIndexColumn = 3;
    var returnDataIfIsThunderbird = function(data, type, full) {
        if (full.name.indexOf('Thunderbird') > -1) {
            return data;
        }

        return null;
    };

    var yesIfDataIsNotNull = function(data, type, full) {
        if (data) {
            return 'Yes';
        }

        return 'No';
    };

    var buildl10nLink = function(data, type, full) {
        return '<a style="cursor: pointer; text-decoration: underline;" href="/releases/' + data + '/l10n">Link</a>';
    };

    var commaToNewLine = function(data) {
        return data.replace(/,/g,',\n');
    };

    var buildPromptWaitTimeLabel = function(data, type, full) {
        if (full.name.indexOf('Fennec') > -1) {
            return 'N/A';
        } else if (!data) {
            return 'Default';
        }

        return data;
    };

    var buildCommentCell = function(data, type, full) {
        if (data && data.length > 50) {
            return '<a href="/releases/' + full.name + '/comment" style="cursor: pointer; text-decoration: underline;">Link</a>';
        }

        return data == null ? '-' : data;
    };

    $('#reviewed').DataTable({
        'bJQueryUI': true,
        'bServerSide': true,
        'sAjaxSource': '/releases/releaseslist',
        'sAjaxDataProp': 'releases',
        'aaSorting': [[submittedAtIndexColumn,'desc']],
        'fnServerParams': function(aoData) {
            aoData.push({'name': 'ready', 'value': true}, {'name': 'complete', 'value': false}, {'name': 'datatableVersion', 'value': this.DataTable.version});
        },
        'aoColumns': [
            {'mData': 'status'},
            {'mData': 'name'},
            {'mData': 'submitter'},
            {'mData': 'submittedAt', 'bSearchable': false},
            {'mData': 'branch'},
            {'mData': 'mozillaRevision'},
            {'mData': 'mozillaRelbranch'},
            {'mData': 'commRevision', 'sDefaultContent': 'N/A', 'mRender': returnDataIfIsThunderbird},
            {'mData': 'commRelbranch', 'sDefaultContent': 'N/A', 'mRender': returnDataIfIsThunderbird},
            {'mData': 'dashboardCheck', 'mRender': yesIfDataIsNotNull},
            {'mData': 'name', 'mRender': buildl10nLink},
            {'mData': 'partials',
             'sDefaultContent': 'N/A',
            'mRender': function(data, type, full) {
                if (data && full.name.indexOf('Fennec') > -1) {
                    return commaToNewLine(data);
                }

                return null;
            }},
            {'mData': 'promptWaitTime', 'mRender': buildPromptWaitTimeLabel},
            {'mData': 'mh_changeset', 'sDefaultContent': 'N/A'},
            {'mData': 'comment', 'mRender': buildCommentCell}
        ]
        ,
        'fnDrawCallback': function(oSettings) {
            setTimeout(function() {
                var width = $('.ui-accordion-header').innerWidth();
                $('#tabContainer').width(width);
            });
        }
    });

    $('#running').DataTable({
        'bJQueryUI': true,
        'bServerSide': true,
        'sAjaxSource': '/releases/releaseslist',
        'sAjaxDataProp': 'releases',
        'aaSorting': [[submittedAtIndexColumn,'desc']],
        'fnServerParams': function(aoData) {
            aoData.push({'name': 'ready', 'value': true}, {'name': 'complete', 'value': true}, {'name': 'datatableVersion', 'value': this.DataTable.version});
        },
        'fnCreatedRow': function(nRow, aData, iDataIndex) {
            var description = aData.description != null ? aData.description : '';
            var htmlDescription = description;

            if (aData.isSecurityDriven) {
                htmlDescription += '<br /><strong style="white-space: nowrap;">Security Driven</strong>';
            }

            htmlDescription += '<div style="cursor: pointer; text-decoration: underline;" class="linkUpdate' + iDataIndex + '"><a target="' + iDataIndex + '" class="showLinkUpdate">Update</a></div>';
            htmlDescription += '<div id="description' + iDataIndex + '" style="display: none;" class="form-group textareaDiv">';
            htmlDescription += '<textarea id="desc' + iDataIndex + '" name="desc' + iDataIndex + '">' + description + '</textarea>';
            htmlDescription += '<div class="checkbox"><label style="white-space: nowrap; font-weight: bold; text-align: center;" for="isSecurityDriven{{ loop.index }}">';
            htmlDescription += '<input type="checkbox" ' + (aData.isSecurityDriven ? 'checked' : '') + ' id="isSecurityDriven' + iDataIndex + '"  name="isSecurityDriven' + iDataIndex + '" value="Is Sec Driven?" title="Did we do this release to fix a security issue (chemspill)?"/> Is sec driven?</label></div>';
            htmlDescription += '<input type="submit" value="Update" class="submitButton" onclick="return updateDesc(\'' + aData.name + '\', ' + iDataIndex + ')" /></div>';

            var tdDescription = $(nRow).find('td')[descriptionIndexColumn];
            $(tdDescription).html(htmlDescription);
        },
        'aoColumns': [
            {'mData': 'name', 'bSearchable': false, 'bSortable': false,
             'mRender': function(data, type, full) {
                return '<a class="btn btn-default btn-xs" href="release/' + data + '/edit_release.html">Edit</a>';
            }},
            {'mData': 'status',
             'mRender': function(data, type, full) {
                if (data == 'Complete') {
                    return '<span class="status_complete">' + data + '</span>';
                }

                return data;
            }},
            {'mData': 'name'},
            {'mData':  'description'},
            {'mData': 'submitter'},
            {'mData': 'submittedAt', 'bSearchable': false,
             'mRender': function(data, type, full) {
                return '<span style="white-space: nowrap;" class="dateDisplay">' + data + '</span>';
            }},
            {'mData': 'branch'},
            {'mData': 'mozillaRevision'},
            {'mData': 'mozillaRelbranch'},
            {'mData': 'commRevision', 'sDefaultContent': 'N/A'},
            {'mData': 'commRelbranch', 'sDefaultContent': 'N/A'},
            {'mData': 'dashboardCheck', 'sDefaultContent': 'N/A'},
            {'mData': 'name', 'mRender': buildl10nLink},
            {'mData': 'partials',
             'mRender': function(data, type, full) {
                if (data) {
                    return commaToNewLine(data);
                }

                return '';
            }},
            {'mData': 'promptWaitTime', 'mRender': buildPromptWaitTimeLabel},
            {'mData': 'mh_changeset', 'sDefaultContent': 'N/A'},
            {'mData': 'comment', 'mRender': buildCommentCell},
            {'mData': 'shippedAt', 'bSearchable': false,
             'mRender': function(data, type, full) {
                return '<span class="dateDisplay">' + data + '</span>';
            }},
            {'mData': 'status',
             'mRender': function(data, type, full) {
                if (full.status !== 'postrelease' && full.status !== 'Post Release') {
                    if (full.ReleaseMarkedAsShipped) {
                        return 'Other build shipped';
                    } else {
                        return 'Not shipped <input type="submit" value="Shipped!" class="submitButton" onclick="return updateShip(\'' + full.name + '\', true)" />';
                    }
                } else {
                    return 'Shipped <input type="submit" value="Not Shipped" class="submitButton" onclick="return updateShip(\'' + full.name + '\', false)" />';
                }

            }}
        ],
        'fnDrawCallback': function(oSettings) {
            toLocalDate();
            setTimeout(function() {
                var width = $('.ui-accordion-header').innerWidth();
                $('#tabContainer').width(width);
            });
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
        if ($(this).prop('tagName') == 'TD' || $(this).prop('tagName') == 'SPAN') {
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

function releaseIsShippedCheckbox() {
    if ($('#isShipped').is(':checked')) {
        $('.shippedDateInfo').css('display', 'block');
    } else {
        $('.shippedDateInfo').css('display', 'none');
    }
}

function editRelease() {
    $('#shippedAtDate').datepicker({dateFormat: 'yy/mm/dd'});
    $('#shippedAtTime').mask('00:00:00');

    releaseIsShippedCheckbox();

    $('#isShipped').change(releaseIsShippedCheckbox);
}
