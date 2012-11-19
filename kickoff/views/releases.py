from flask import request, jsonify, render_template, Response, redirect
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField, StringField, SelectMultipleField, \
  ListWidget, CheckboxInput

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease, \
  getReleaseTable, getReleases, Release

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

class ReleasesAPI(MethodView):
    def get(self):
        ready = request.args.get('ready', None, type=int)
        complete = request.args.get('complete', None, type=int)
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

class Releases(MethodView):
    def get(self):
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
        releases=sorted(getReleases(), cmp=sortReleases)
        # We should really be creating a Form here and letting it render
        # rather than rendering by hand in the template, but it seems that's
        # not possible without some heavy handed subclassing. For our simple
        # case it's not worthwhile
        # http://stackoverflow.com/questions/8463421/how-to-render-my-select-field-with-wtforms
        #form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        form = ReadyForm()
        return render_template('releases.html', releases=releases, form=form)

    def post(self):
        submitter = request.environ.get('REMOTE_USER')
        form = ReadyForm()
        form.readyReleases.choices = [(r.name, r.name) for r in getReleases(ready=False)]
        if not form.validate():
            return Response(status=400, response=form.errors)

        for release in form.readyReleases.data:
            table = getReleaseTable(release)
            r = table.query.filter_by(name=release).first()
            r.ready = True
            r.status = 'Pending'
            db.session.add(r)
        db.session.commit()
        return redirect('releases.html')
