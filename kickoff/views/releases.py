from flask import request, jsonify, render_template, Response, redirect
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField, StringField

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease, \
  getReleaseTable, getReleases

class CompleteForm(Form):
    complete = BooleanField('complete')
    status = StringField('status')

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
            # After that, sort by name
            if x.ready:
                if y.ready:
                    return cmp(x.name, y.name)
                else:
                    return 1
            elif y.ready:
                return -1
            if x.complete:
                if y.complete:
                    return cmp(x.name, y.name)
                else:
                    return 1
            elif y.complete:
                return -1
            return cmp(x.name, y.name)
        releases=sorted(getAllReleases(), cmp=sortReleases)
        print releases
        return render_template('releases.html', releases=releases)

    def post(self):
        submitter = request.environ.get('REMOTE_USER')
        for release, ready in request.form.iteritems():
            if ready:
                table = getReleaseTable(release)
                r = table.query.filter_by(name=release).first()
                r.ready = True
                db.session.add(r)
        db.session.commit()
        return redirect('releases.html')
