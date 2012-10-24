from flask import request, render_template, Response, redirect, make_response
from flask.views import MethodView

from flask.ext.wtf import Form, TextField, DataRequired, BooleanField, IntegerField

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease

class ReleaseForm(Form):
    fennec = BooleanField('Fennec')
    firefox = BooleanField('Firefox')
    thunderbird = BooleanField('Thunderbird')
    version = TextField('Version:', validators=[DataRequired('Version is required.')])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired('Build number is required.')])
    mozillaRevision = TextField('Mozilla Revision:', validators=[DataRequired('Mozilla revision is required.')])
    commRevision = TextField('Comm Revision:')
    fennecL10nChangesets = TextField('Fennec L10n Changesets:')
    firefoxL10nChangesets = TextField('Firefox L10n Changesets:')
    thunderbirdL10nChangesets = TextField('Thunderbird L10n Changesets:')
    firefoxPartials = TextField('Firefox partial versions (eg, 17.0b2build1):')
    thunderbirdPartials = TextField('Thunderbird partial versions:')

class SubmitRelease(MethodView):
    def get(self):
        return render_template('submit_release.html', form=ReleaseForm())

    def post(self):
        submitter = request.environ.get('REMOTE_USER')
        form = ReleaseForm()
        errors = []
        if not form.validate():
            for errlist in form.errors.values():
                errors.extend(errlist)
        if not form.fennec.data and not form.firefox.data and not form.thunderbird.data:
            errors.append("Must select at least one product.")

        if form.fennec.data:
            if not form.fennecL10nChangesets.data:
                errors.append("L10n changesets is required for Fennec")
            release = FennecRelease(submitter, form.version.data,
                form.buildNumber.data, form.mozillaRevision.data,
                form.fennecL10nChangesets.data)
            db.session.add(release)

        if form.firefox.data:
            if not form.firefoxL10nChangesets.data:
                errors.append("L10n changesets are requried for Firefox.")
            if not form.firefoxPartials.data:
                errors.append("Partial versions are required for Firefox.")
            release = FirefoxRelease(form.firefoxPartials.data, submitter,
                form.version.data, form.buildNumber.data,
                form.mozillaRevision.data, form.firefoxL10nChangesets.data)
            db.session.add(release)

        if form.thunderbird.data:
            if not form.commRevision.data:
                errors.append("Comm revision is required for Thunderbird.")
            if not form.thunderbirdL10nChangesets.data:
                errors.append("L10n changesets are required for Thunderbird.")
            if not form.thunderbirdPartials.data:
                errors.append("Partial versions are required for Thunderbird.")
            release = ThunderbirdRelease(form.commRevision.data,
                form.thunderbirdPartials.data, submitter, form.version.data,
                form.buildNumber.data, form.mozillaRevision.data,
                form.thunderbirdL10nChangesets.data)
            db.session.add(release)

        if errors:
            return make_response(render_template('submit_release.html', errors=errors, form=ReleaseForm()), 400)
        else:
            db.session.commit()
            return redirect('releases.html')
