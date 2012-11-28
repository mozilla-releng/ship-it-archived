import simplejson as json

from flask import request, render_template, Response, redirect, make_response
from flask.views import MethodView

from flask.ext.wtf import Form, TextField, DataRequired, BooleanField, IntegerField, TextAreaField, Regexp, Optional

from mozilla.build.versions import ANY_VERSION_REGEX

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease

PARTIAL_VERSIONS_REGEX = ('^(%sbuild\d+),(%sbuild\d)*$' % (ANY_VERSION_REGEX, ANY_VERSION_REGEX))

class JSONField(TextAreaField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = valuelist[0]
            try:
                # We only care about whether the JSON validates or not, so
                # we don't save this anywhere. Consumers of the form want the
                # raw string version, not the parsed object.
                json.loads(self.data)
            except ValueError, e:
                self.process_errors.append(e.args[0])
        else:
            self.data = None

class ReleaseForm(Form):
    fennec = BooleanField('Fennec')
    firefox = BooleanField('Firefox')
    thunderbird = BooleanField('Thunderbird')
    version = TextField('Version:', validators=[Regexp(ANY_VERSION_REGEX, message='Invalid version format.')])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired('Build number is required.')])
    branch = TextField('Branch:', validators=[DataRequired('Branch is required')])
    mozillaRevision = TextField('Mozilla Revision:', validators=[DataRequired('Mozilla revision is required.')])
    # TODO: make these required/validated after splitting into 3 dfferent forms
    commRevision = TextField('Comm Revision:')
    fennecL10nChangesets = JSONField('Fennec L10n Changesets:')
    firefoxL10nChangesets = TextAreaField('Firefox L10n Changesets:')
    thunderbirdL10nChangesets = TextAreaField('Thunderbird L10n Changesets:')
    dashboardCheck = BooleanField('Check l10n revisions against dashboard?', default=True)
    # TODO: Remove Optional validators when form is split into 3 different ones
    firefoxPartials = TextField('Firefox partial versions (eg, 17.0b1build2,17.0b2build1):',
        validators=[Optional(), Regexp(ANY_VERSION_REGEX, message='Invalid partials format for Firefox')]
    )
    thunderbirdPartials = TextField('Thunderbird partial versions:',
        validators=[Optional(), Regexp(ANY_VERSION_REGEX, message='Invalid partials format for Thunderbird')]
    )

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
                form.buildNumber.data, form.branch.data,
                form.mozillaRevision.data, form.fennecL10nChangesets.data,
                form.dashboardCheck.data)
            db.session.add(release)

        if form.firefox.data:
            if not form.firefoxL10nChangesets.data:
                errors.append("L10n changesets are requried for Firefox.")
            if not form.firefoxPartials.data:
                errors.append("Partial versions are required for Firefox.")
            release = FirefoxRelease(form.firefoxPartials.data, submitter,
                form.version.data, form.buildNumber.data,
                form.branch.data, form.mozillaRevision.data,
                form.firefoxL10nChangesets.data, form.dashboardCheck.data)
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
                form.buildNumber.data, form.branch.data,
                form.mozillaRevision.data, form.thunderbirdL10nChangesets.data,
                form.dashboardCheck.data)
            db.session.add(release)

        if errors:
            return make_response(render_template('submit_release.html', errors=errors, form=ReleaseForm()), 400)
        else:
            db.session.commit()
            return redirect('releases.html')
