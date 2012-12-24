from flask import request, jsonify, render_template, Response, redirect, make_response
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField, StringField, SelectMultipleField, \
  ListWidget, CheckboxInput, Length

from kickoff import db
from kickoff.model import getReleaseTable, getReleases, Release

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ReadyForm(Form):
    readyReleases = MultiCheckboxField('readyReleases')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

class CompleteForm(Form):
    complete = BooleanField('complete')
    # Use the Column length directly rather than duplicating its value.
    status = StringField('status', [Length(max=Release.status.type.length)])

def sortedRelease():
    def sortReleases(x, y):
        # Not ready releases should come before ready ones.
        # Incomplete releases should come before completed ones.
        # After that, sort by name.
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
        return cmp(x.name, y.name)
    return sorted(getReleases(), cmp=sortReleases)

class ReleasesAPI(MethodView):
    def get(self):
        # We can't get request.args to convert directly to a bool because
        # it will convert even if the arg isn't present! In these cases
        # we need to be able to pass along a None, so we must be a bit
        # roundabout here.
        try:
            ready = request.args.get('ready', type=int)
            if ready is not None:
                ready = bool(ready)
            complete = request.args.get('complete', type=int)
            if complete is not None:
                complete = bool(complete)
        except ValueError:
            return Response(status=400, response="Got unparseable value for ready or complete")
        releases = [r.name for r in getReleases(ready, complete)]
        return jsonify({'releases': releases})

class ReleaseAPI(MethodView):
    def get(self, releaseName):
        table = getReleaseTable(releaseName)
        return jsonify(table.query.filter_by(name=releaseName).first().toDict())

    def post(self, releaseName):
        table = getReleaseTable(releaseName)
        form = CompleteForm()
        if not form.validate():
            return Response(status=400, response=form.errors)

        release = table.query.filter_by(name=releaseName).first()
        if form.complete.data:
            release.complete = form.complete.data
        if form.status.data:
            release.status = form.status.data
        db.session.add(release)
        db.session.commit()
        return Response(status=200)

class ReleaseL10nAPI(MethodView):
    def get(self, releaseName):
        table = getReleaseTable(releaseName)
        l10n = table.query.filter_by(name=releaseName).first().l10nChangesets
        return Response(status=200, response=l10n, content_type='text/plain')

class Releases(MethodView):
    def get(self):
        # We should really be creating a Form here and letting it render
        # rather than rendering by hand in the template, but it seems that's
        # not possible without some heavy handed subclassing. For our simple
        # case it's not worthwhile
        # http://stackoverflow.com/questions/8463421/how-to-render-my-select-field-with-wtforms
        #form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        form = ReadyForm()
        return render_template('releases.html', releases=sortedRelease(), form=form)

    def post(self):
        form = ReadyForm()
        form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        if not form.validate():
            form = ReadyForm()
            return make_response(render_template('releases.html', errors=form.errors, releases=sortedRelease(), form=form))

        for release in form.readyReleases.data:
            table = getReleaseTable(release)
            r = table.query.filter_by(name=release).first()
            r.ready = True
            r.status = 'Pending'
            db.session.add(r)
        db.session.commit()
        return redirect('releases.html')
