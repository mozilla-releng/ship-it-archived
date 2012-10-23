from flask import request, jsonify, render_template, Response
from flask.views import MethodView

from flask.ext.wtf import Form, BooleanField

from kickoff import app, db
from kickoff.model import Release

class CompleteForm(Form):
    complete = BooleanField('complete')

class RequestsAPI(MethodView):
    def get(self):
        releases = {}
        if request.args.get('incomplete'):
            for r in Release.query.filter_by(complete=False):
                releases[r.name] = r.toDict()
        else:
            for r in Release.query.all():
                releases[r.name] = r.toDict()
        return jsonify(releases)

class ReleaseAPI(MethodView):
    def post(self, releaseName):
        form = CompleteForm()
        if not form.validate():
            return Response(status=400, response=form.errors)

        release = Release.query.filter_by(name=releaseName).first()
        release.complete = form.complete.data
        db.session.add(release)
        db.session.commit()
        return Response(200)

class Requests(MethodView):
    def get(self):
        return render_template('requests.html', releases=Release.query.all())
