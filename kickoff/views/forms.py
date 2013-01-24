from ast import literal_eval
import logging
import simplejson as json

from flask.ext.wtf import SelectMultipleField, ListWidget, CheckboxInput, \
    Form, BooleanField, StringField, Length, TextAreaField, DataRequired, \
    IntegerField, HiddenField, Regexp

from mozilla.build.versions import ANY_VERSION_REGEX
from mozilla.release.l10n import parsePlainL10nChangesets

from kickoff.model import Release

log = logging.getLogger(__name__)


# From http://wtforms.simplecodes.com/docs/1.0.2/specific_problems.html#specialty-field-tricks
class MultiCheckboxField(SelectMultipleField):
    """A multiple-select, except displays a list of checkboxes. Iterating the
       field will produce subfields, allowing custom rendering of the enclosed
       checkbox fields."""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ThreeStateField(StringField):
    """Similar to a BooleanField, but supports the abscence of data. If the
       field is absent completely data is None. Otherwise ast.literal_eval
       is used to get a boolean value from the data."""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = bool(literal_eval(valuelist[0]))
        else:
            self.data = None


class ReleasesForm(Form):
    readyReleases = MultiCheckboxField('readyReleases')
    deleteReleases = MultiCheckboxField('deleteReleases')

    def validate(self, *args, **kwargs):
        valid = Form.validate(self, *args, **kwargs)
        readyAndDeleted = set(self.readyReleases.data).intersection(self.deleteReleases.data)
        if readyAndDeleted:
            valid = False
            msg = 'Cannot delete releases that were also marked as ready: '
            msg += ', '.join([r[0] for r in readyAndDeleted])
            if 'deleteReleases' not in self.errors:
                self.errors['deleteReleases'] = []
            self.errors['deleteReleases'].append(msg)

        return valid


class ReleaseAPIForm(Form):
    ready = ThreeStateField('ready')
    complete = ThreeStateField('complete')
    # Use the Column length directly rather than duplicating its value.
    status = StringField('status', [Length(max=Release.status.type.length)])

    def validate(self, release, *args, **kwargs):
        valid = Form.validate(self, *args, **kwargs)
        # Completed releases shouldn't be altered in terms of readyness or
        # completeness. Status updates are OK though.
        if release.complete:
            if self.ready.data is False or self.complete.data is False:
                valid = False
                if 'ready' not in self.errors:
                    self.errors['ready'] = []
                self.errors['ready'].append('Cannot make a completed release not ready or incomplete.')
        # If the release isn't complete, we can accept changes to readyness or
        # completeness, but marking a release as not ready *and* complete at
        # the same time is invalid.
        else:
            if self.ready.data is False and self.complete.data is True:
                valid = False
                if 'ready' not in self.errors:
                    self.errors['ready'] = []
                self.errors['ready'].append('A release cannot be made ready and complete at the same time')

        return valid

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
                log.info("JSON in field '%s' didn't validate" % self.name)
                log.debug("Raw JSON for '%s' is: %s" % (self.name, repr(self.data)))
                self.process_errors.append(e.args[0])
        else:
            self.data = None


class PlainChangesetsField(TextAreaField):
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = valuelist[0]
            try:
                # Like the JSON object, we merely care about if the data
                # is valid or not, so we don't save the results anywhere.
                parsePlainL10nChangesets(self.data)
            except ValueError:
                self.process_errors.append('Bad format in %s field' % self.name)
        else:
            self.data = None


def noneFilter(value):
    """Filters empty strings into null values. Used for non-required fields
       like relbranches where "None" means "use the default"."""
    if not value:
        value = None
    return value


class ReleaseForm(Form):
    version = StringField('Version:', validators=[Regexp(ANY_VERSION_REGEX, message='Invalid version format.')])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired('Build number is required.')])
    branch = StringField('Branch:', validators=[DataRequired('Branch is required')])
    mozillaRevision = StringField('Mozilla Revision:', validators=[DataRequired('Mozilla revision is required.')])
    dashboardCheck = BooleanField('Dashboard check?', default=True)
    mozillaRelbranch = StringField('Mozilla Relbranch:', filters=[noneFilter])


class FennecReleaseForm(ReleaseForm):
    product = HiddenField('product')
    l10nChangesets = JSONField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='fennec', product='fennec', *args, **kwargs)

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        self.mozillaRevision.data = row.mozillaRevision
        self.dashboardCheck.data = row.dashboardCheck
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch


def collapseSpaces(value):
    """A filter that collapses spaces within a string. Used for the "partials"
       field to make the formatting slightly less strict."""
    # It's not clear to me why, but this filter sometimes gets passed empty
    # None rather than a string. The tests confirm that the filter is working
    # though...
    if value:
        value = value.replace(' ', '')
    return value


class NullableIntegerField(IntegerField):
    """Just like an IntegerField, except an empty value is allowed."""
    def process_formdata(self, valuelist):
        if valuelist and not valuelist[0]:
            valuelist = None
        return IntegerField.process_formdata(self, valuelist)


class DesktopReleaseForm(ReleaseForm):
    partials = StringField('Partial versions:',
        validators=[Regexp(PARTIAL_VERSIONS_REGEX, message='Invalid partials format.')],
        filters=[collapseSpaces],
    )
    promptWaitTime = NullableIntegerField('Update prompt wait time:')
    l10nChangesets = PlainChangesetsField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])


class FirefoxReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='firefox', product='firefox', *args, **kwargs)

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        self.mozillaRevision.data = row.mozillaRevision
        self.partials.data = row.partials
        self.promptWaitTime.data = row.promptWaitTime
        self.dashboardCheck.data = row.dashboardCheck
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch


class ThunderbirdReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')
    commRevision = StringField('Comm Revision:', validators=[DataRequired('Comm revision is required.')])
    commRelbranch = StringField('Comm Relbranch:', filters=[noneFilter])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='thunderbird', product='thunderbird', *args, **kwargs)

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        self.mozillaRevision.data = row.mozillaRevision
        self.commRevision.data = row.commRevision
        self.partials.data = row.partials
        self.promptWaitTime.data = row.promptWaitTime
        self.dashboardCheck.data = row.dashboardCheck
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch
        self.commRelbranch.data = row.commRelbranch


def getReleaseForm(release):
    """Helper method to figure out which form is needed for a release, based
       on its name."""
    release = release.lower()
    if release.startswith('fennec'):
        return FennecReleaseForm
    elif release.startswith('firefox'):
        return FirefoxReleaseForm
    elif release.startswith('thunderbird'):
        return ThunderbirdReleaseForm
    else:
        raise ValueError("Can't find release table for release %s" % release)
