import simplejson as json

from flask import request, render_template, Response, redirect, make_response
from flask.views import MethodView

from flask.ext.wtf import Form, TextField, DataRequired, BooleanField, IntegerField, TextAreaField, HiddenField, Regexp, Optional

from mozilla.build.versions import ANY_VERSION_REGEX

from kickoff import app, db
from kickoff.model import FennecRelease, FirefoxRelease, ThunderbirdRelease, getReleaseTable

PARTIAL_VERSIONS_REGEX = ('^(%sbuild\d+)(,%sbuild\d)*$' % (ANY_VERSION_REGEX, ANY_VERSION_REGEX))

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
    version = TextField('Version:', validators=[Regexp(ANY_VERSION_REGEX, message='Invalid version format.')])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired('Build number is required.')])
    branch = TextField('Branch:', validators=[DataRequired('Branch is required')])
    mozillaRevision = TextField('Mozilla Revision:', validators=[DataRequired('Mozilla revision is required.')])
    dashboardCheck = BooleanField('Dashboard check?', default=True)

class FennecReleaseForm(ReleaseForm):
    product = HiddenField('product')
    l10nChangesets = JSONField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='fennec', product='fennec', *args, **kwargs)

class DesktopReleaseForm(ReleaseForm):
    partials = TextField('Partial versions:',
        validators=[Regexp(PARTIAL_VERSIONS_REGEX, message='Invalid partials format.')]
    )
    l10nChangesets = TextAreaField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

class FirefoxReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='firefox', product='firefox', *args, **kwargs)

class ThunderbirdReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')
    commRevision = TextField('Comm Revision:', validators=[DataRequired('Comm revision is required.')])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='thunderbird', product='thunderbird', *args, **kwargs)

class SubmitRelease(MethodView):
    def get(self):
        return render_template('submit_release.html', fennecForm=FennecReleaseForm(),
            firefoxForm=FirefoxReleaseForm(), thunderbirdForm=ThunderbirdReleaseForm())

    def post(self):
        submitter = request.environ.get('REMOTE_USER')
        forms = {
            'fennecForm': FennecReleaseForm(formdata=None),
            'firefoxForm': FirefoxReleaseForm(formdata=None),
            'thunderbirdForm': ThunderbirdReleaseForm(formdata=None)
        }
        for field, value in request.form.items():
            if field.endswith('product'):
                product = value
                break
        if product == 'fennec':
            form = forms['fennecForm'] = FennecReleaseForm()
        elif product == 'firefox':
            form = forms['firefoxForm'] = FirefoxReleaseForm()
        elif product == 'thunderbird':
            form = forms['thunderbirdForm'] = ThunderbirdReleaseForm()
        errors = []
        if not form.validate():
            for errlist in form.errors.values():
                errors.extend(errlist)
        if errors:
            return make_response(render_template('submit_release.html', errors=errors, **forms), 400)

        table = getReleaseTable(form.product.data)
        release = table.createFromForm(submitter, form)
        db.session.add(release)
        db.session.commit()
        return redirect('releases.html')
