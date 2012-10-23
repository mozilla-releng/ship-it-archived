from flask import request, jsonify, render_template, Response
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField

from kickoff import app, db
from kickoff.model import Release

class CompleteForm(Form):
    complete = BooleanField('complete')

class ReleasesAPI(MethodView):
    def get(self):
        releases = []
        if request.args.get('incomplete'):
            for r in Release.query.filter_by(complete=False):
                releases.append(r.name)
        else:
            for r in Release.query.all():
                releases.append(r.name)
        return jsonify({'releases': releases})

class ReleaseAPI(MethodView):
    def get(self, releaseName):
        return jsonify(Release.query.filter_by(name=releaseName).first().toDict())

    def post(self, releaseName):
        form = CompleteForm()
        if not form.validate():
            return Response(status=400, response=form.errors)

        release = Release.query.filter_by(name=releaseName).first()
        release.complete = form.complete.data
        db.session.add(release)
        db.session.commit()
        return Response(200)

class Releases(MethodView):
    def get(self):
        return render_template('releases.html', releases=Release.query.all())
