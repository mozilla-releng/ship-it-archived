from flask import request, render_template, Response, redirect
from flask.views import MethodView

from flask.ext.wtf import Form, TextField, DataRequired, BooleanField, IntegerField

from kickoff import app, db
from kickoff.model import Release

class ReleaseForm(Form):
    fennec = BooleanField('Fennec')
    firefox = BooleanField('Firefox')
    thunderbird = BooleanField('Thunderbird')
    version = TextField('Version:', validators=[DataRequired()])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired()])
    mozillaRevision = TextField('Mozilla Revision:', validators=[DataRequired()])
    commRevision = TextField('Comm Revision:')
    fennecL10nChangesets = TextField('Fennec L10n Changesets:')
    firefoxL10nChangesets = TextField('Firefox L10n Changesets:')
    thunderbirdL10nChangesets = TextField('Thunderbird L10n Changesets:')
    partials = TextField('Partial versions (comma separated):')
    whatsnew = BooleanField('Show whatsnew page?')

class SubmitRelease(MethodView):
    def get(self):
        return render_template('submit_release.html', form=ReleaseForm())

    def post(self):
        submitter = request.environ.get('REMOTE_USER', 'REMOVEME')
        form = ReleaseForm()
        if not form.validate():
            return Response(status=400, response=form.errors)
        if not form.fennec.data and not form.firefox.data and not form.thunderbird.data:
            return Response(status=400, response="Must select at least one product.")

        if form.fennec.data:
            release = Release(submitter, 'fennec', form.version.data,
                form.buildNumber.data, form.mozillaRevision.data,
                form.fennecL10nChangesets.data, form.partials.data,
                form.whatsnew.data)
            db.session.add(release)
        if form.firefox.data:
            release = Release(submitter, 'firefox', form.version.data,
                form.buildNumber.data, form.mozillaRevision.data,
                form.firefoxL10nChangesets.data, form.partials.data,
                form.whatsnew.data)
            db.session.add(release)
        if form.thunderbird.data:
            release = Release(submitter, 'thunderbird', form.version.data,
                form.buildNumber.data, form.mozillaRevision.data,
                form.firefoxL10nChangesets.data, form.partials.data,
                form.whatsnew.data, commRevision=form.commRevision.data)
            db.session.add(release)

        db.session.commit()
        return redirect('requests.html')
