from flask import request, jsonify, render_template, Response
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease, \
  getReleaseTable

class CompleteForm(Form):
    complete = BooleanField('complete')

def getReleases(incompleteOnly=False):
    releases = []
    for table in (FennecRelease, FirefoxRelease, ThunderbirdRelease):
        if incompleteOnly:
            for r in table.query.filter_by(complete=False):
                releases.append(r)
        else:
            for r in table.query.all():
                releases.append(r)
    return releases

class ReleasesAPI(MethodView):
    def get(self):
        releases = [r.name for r in getReleases(request.args.get('incomplete'))]
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
        release.complete = form.complete.data
        db.session.add(release)
        db.session.commit()
        return Response(status=200)

class Releases(MethodView):
    def get(self):
        releases=sorted(getReleases(), cmp=lambda x,y: cmp(x.complete, y.complete))
        return render_template('releases.html', releases=releases)
