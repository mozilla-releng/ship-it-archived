import logging

from flask import request, jsonify, render_template, Response, redirect, \
    make_response, abort
from flask.views import MethodView

from kickoff import db
from kickoff.log import cef_event, CEF_WARN, CEF_INFO
from kickoff.model import getReleaseTable, getReleases, getReleasesListView, ProductReleasesView, ReleasesPaginationCriteria
from kickoff.views.forms import ReleasesForm, ReleaseAPIForm, getReleaseForm, EditReleaseForm

log = logging.getLogger(__name__)


def sortedReleases(ready=None):
    def cmpReleases(x, y):
        # Not ready releases should come before ready ones.
        # Incomplete releases should come before completed ones.
        # After that, sort by submission time
        # Newer releases should be at the top.
        if x.ready:
            if not y.ready:
                return 1
        elif y.ready:
            return -1
        if x.complete:
            if not y.complete:
                return 1
        elif y.complete:
            return -1
        return cmp(y._submittedAt, x._submittedAt)  # NOQA
    return sorted(getReleases(ready=ready), cmp=cmpReleases)


class ReleasesAPI(MethodView):
    def get(self):
        # We can't get request.args to convert directly to a bool because
        # it will convert even if the arg isn't present! In these cases
        # we need to be able to pass along a None, so we must be a bit
        # roundabout here.
        try:
            ready = request.args.get('ready', type=int)
            complete = request.args.get('complete', type=int)
            if ready is not None:
                ready = bool(ready)
            if complete is not None:
                complete = bool(complete)
        except ValueError:
            cef_event('User Input Failed', CEF_INFO, ready=ready, complete=complete)
            return Response(status=400, response="Got unparseable value for ready or complete")
        releases = [r.name for r in getReleases(ready, complete)]
        return jsonify({'releases': releases})


class ReleaseAPI(MethodView):
    def get(self, releaseName):
        table = getReleaseTable(releaseName)
        return jsonify(table.query.filter_by(name=releaseName).first().toDict())

    def post(self, releaseName):
        table = getReleaseTable(releaseName)
        release = table.query.filter_by(name=releaseName).first()
        form = ReleaseAPIForm()
        if not form.validate(release):
            errors = form.errors
            cef_event('User Input Failed', CEF_INFO, **errors)
            errorsStr = ', '.join("%s" % val[0] for val in errors.values())
            return Response(status=400, response=errorsStr)

        # All of the validation has already been done by the form so we can
        # safely assume that the values we have are valid.
        if form.ready.data is not None:
            log.debug('%s: ready being changed to: %s', releaseName, form.ready.data)
            release.ready = form.ready.data
        if form.complete.data is not None:
            log.debug('%s: complete being changed to: %s', releaseName, form.complete.data)
            release.complete = form.complete.data
        if form.status.data:
            log.debug('%s: status being changed to: %s', releaseName, form.status.data)
            release.status = form.status.data
        if form.description.data:
            log.debug('%s: description being changed to: %s', releaseName, form.description.data)
            release.description = form.description.data
            log.debug('%s: isSecurityDriven being changed to: %s', releaseName, form.isSecurityDriven.data)
            release.isSecurityDriven = form.isSecurityDriven.data
        else:
            # Don't do when we are updating the desc, it would reset the date
            log.debug('%s: shippedAt being changed to: %s', releaseName, form.shippedAt.data)
            release.shippedAt = form.shippedAt.data

        db.session.add(release)
        db.session.commit()
        return Response(status=200)


class ReleasesListAPI(MethodView):
    def __init__(self):
        self.dataTableVersion = '1.9.4'
        self.sortColumnIndexPrefix = 'iSortCol_'
        self.sortColumnDirectionPrefix = 'sSortDir_'
        self.columnNamePrefix = 'mDataProp_'
        self.columnCountParam = 'iColumns'
        self.serchablePrefix = 'bSearchable_'
        self.searchParam = 'sSearch'

    def checkJQueryDataTableVersion(self):
        version = request.args.get('datatableVersion')

        if version is None or self.dataTableVersion not in version:
            msg = str.format('The Jquery datatable version is {0}. Expected version 1.9.4', version)
            log.warning(msg)

    def getOrderByDict(self):
        # Warning: This is a server-side function that is highly dependent of Jquery Datatables
        self.checkJQueryDataTableVersion()

        order_by = {
            'ready': 'asc',
            'complete': 'asc'
        }

        columnCount = request.args.get(self.columnCountParam, type=int)

        for i in range(0, columnCount):
            sortIndex = request.args.get(self.sortColumnIndexPrefix + str(i))

            if sortIndex is None:
                break

            name = request.args.get(self.columnNamePrefix + sortIndex)
            direction = request.args.get(self.sortColumnDirectionPrefix + str(i))
            order_by[name] = direction

        return order_by

    def getSearchFilterDict(self):
        # Warning: This is a server-side function that is highly dependent of Jquery Datatables
        self.checkJQueryDataTableVersion()

        searchFilter = {}

        columnCount = request.args.get(self.columnCountParam, type=int)
        param = request.args.get(self.searchParam)

        if param and not param.isspace():
            for filterIndex in range(columnCount):
                if request.args.get(self.serchablePrefix + str(filterIndex)) == 'true':
                    columnName = request.args.get(self.columnNamePrefix + str(filterIndex))
                    searchFilter[columnName] = param

        return searchFilter

    def get(self):
        start = request.args.get('iDisplayStart', type=int)
        length = request.args.get('iDisplayLength', type=int)

        readyParam = request.args.get('ready')
        completeParam = request.args.get('complete')

        ready = None
        complete = None

        if readyParam is not None:
            ready = readyParam == 'true'
        if completeParam is not None:
            complete = completeParam == 'true'

        searchFilterDict = self.getSearchFilterDict()
        orderByDict = self.getOrderByDict()
        total = ProductReleasesView.getTotal(complete=complete,
                                             ready=ready,
                                             searchFilter=searchFilterDict)

        paginationCriteria = ReleasesPaginationCriteria(start,
                                                        length,
                                                        orderByDict)

        releases = getReleasesListView(complete=complete,
                                       ready=ready,
                                       paginationCriteria=paginationCriteria,
                                       searchFilter=searchFilterDict)

        paginatedReleases = {
            'releases': [ProductReleasesView.releaseToDict(r) for r in releases],
            'iTotalDisplayRecords': total,
            'iTotalRecords': total
        }

        return jsonify(paginatedReleases)


class ReleaseL10nAPI(MethodView):
    def get(self, releaseName):
        table = getReleaseTable(releaseName)
        release = table.query.filter_by(name=releaseName).first()
        if not release:
            abort(404)
        return Response(status=200, response=release.l10nChangesets,
                        content_type='text/plain')


class ReleaseCommentAPI(MethodView):
    def get(self, releaseName):
        table = getReleaseTable(releaseName)
        release = table.query.filter_by(name=releaseName).first()
        if not release:
            abort(404)
        return Response(status=200, response=release.comment,
                        content_type='text/plain')


class Releases(MethodView):
    def get(self):
        # We should really be creating a Form here and letting it render
        # rather than rendering by hand in the template, but it seems that's
        # not possible without some heavy handed subclassing. For our simple
        # case it's not worthwhile
        # http://stackoverflow.com/questions/8463421/how-to-render-my-select-field-with-wtforms
        # form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        form = ReleasesForm()
        return render_template('releases.html', releases=sortedReleases(ready=False), form=form)

    def post(self):
        starter = request.environ.get('REMOTE_USER')

        form = ReleasesForm()
        form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        # Don't include completed or ready releases, because they aren't allowed to be deleted
        form.deleteReleases.choices = [(r.name, r.name) for r in getReleases(complete=False, ready=False)]
        if not form.validate():
            cef_event('User Input Failed', CEF_WARN, **form.errors)
            return make_response(render_template('releases.html', errors=form.errors, releases=sortedReleases(), form=form), 400)

        for release in form.deleteReleases.data:
            log.debug('%s is being deleted', release)
            table = getReleaseTable(release)
            r = table.query.filter_by(name=release).first()
            db.session.delete(r)
        for release in form.readyReleases.data:
            log.debug('%s is being marked as ready', release)
            table = getReleaseTable(release)
            r = table.query.filter_by(name=release).first()
            r.ready = True
            r.status = 'Pending'
            r.comment = form.comment.data
            r.starter = starter
            db.session.add(r)
        db.session.commit()
        return render_template('releases.html', releases=sortedReleases(ready=False), form=form)


class Release(MethodView):
    def get(self):
        name = request.args.get('name')
        form = getReleaseForm(name)()
        release = getReleaseTable(name).query.filter_by(name=name).first()
        if not release:
            abort(404)
        # If this release is already ready or complete, edits aren't allowed.
        # It would be best to display an error here, but considering that there
        # aren't even links to this page for these releases, redirecting back
        # to the list of release seems OK.
        if release.ready or release.complete:
            return redirect('releases.html')

        # If the release is editable, prepopulate the form with the current
        # values from the database.
        form.updateFromRow(release)
        return render_template('release.html', form=form, release=name)

    def post(self):
        name = request.args.get('name')
        form = getReleaseForm(name)()
        release = getReleaseTable(name).query.filter_by(name=name).first()
        if not release:
            abort(404)
        # Similar to the above, don't allow edits to ready or completed
        # releases. Unless someone has constructed a POST by hand, this code
        # should never be hit.
        if release.ready or release.complete:
            errors = ["Cannot update a release that's been marked as ready or is complete"]
            return make_response(render_template('release.html', errors=errors, form=form, release=name), 403)

        if not form.validate():
            return make_response(render_template('release.html', errors=form.errors.values(), form=form, release=name), 400)

        release.updateFromForm(form)
        db.session.add(release)
        db.session.commit()
        log.debug('%s has been edited', name)
        return redirect('releases.html')


class EditRelease(MethodView):
    def get(self, releaseName):
        releaseTable = getReleaseTable(releaseName)
        release = releaseTable.query.filter_by(name=releaseName).first()

        if not release:
            abort(404)

        formRelease = EditReleaseForm(obj=release, isShipped=release._shippedAt is not None)

        if release._shippedAt:
            formRelease.shippedAtDate.process_data(release._shippedAt)
            strTime = str(release._shippedAt.time())
            formRelease.shippedAtTime.data = strTime

        return render_template('edit_release.html', form=formRelease, release=release)

    def post(self, releaseName):
        releaseTable = getReleaseTable(releaseName)
        release = releaseTable.query.filter_by(name=releaseName).first()

        if not release:
            abort(404)

        form = EditReleaseForm(request.form, release)

        if not form.validate():
            errors = []
            for error in form.errors.values():
                errors.extend(error)

            return make_response(render_template('edit_release.html', errors=errors, form=form, release=release), 400)

        form.populate_obj(release)

        if form.isShipped.data:
            release.shippedAt = form.shippedAt
            release.status = 'shipped'
        else:
            release.shippedAt = None
            release.status = 'Started'

        db.session.add(release)
        db.session.commit()
        return redirect('releases.html')
