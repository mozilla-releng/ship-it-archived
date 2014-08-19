import logging
import re

import simplejson as json
from ast import literal_eval
from collections import defaultdict
from distutils.version import LooseVersion

from flask.ext.wtf import SelectMultipleField, ListWidget, CheckboxInput, \
    Form, BooleanField, StringField, Length, TextAreaField, DataRequired, \
    IntegerField, HiddenField, Regexp, TextInput, DateTimeField, InputRequired

from mozilla.build.versions import ANY_VERSION_REGEX, getPossibleNextVersions
from mozilla.release.l10n import parsePlainL10nChangesets

from kickoff.model import Release, getReleaseTable

log = logging.getLogger(__name__)


PARTIAL_VERSIONS_REGEX = ('^(%sbuild\d+)(,%sbuild\d)*$' % (ANY_VERSION_REGEX, ANY_VERSION_REGEX))
NAME_REGEX = re.compile('\w{0,100}-%s-build\d+' % ANY_VERSION_REGEX)

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
            self.data = valuelist[0].strip()
            try:
                # Like the JSON object, we merely care about if the data
                # is valid or not, so we don't save the results anywhere.
                parsePlainL10nChangesets(self.data)
            except ValueError:
                self.process_errors.append('Bad format in %s field' % self.name)
        else:
            self.data = None


class NullableIntegerField(IntegerField):
    """Just like an IntegerField, except an empty value is allowed."""
    def process_formdata(self, valuelist):
        if valuelist and not valuelist[0]:
            valuelist = None
        return IntegerField.process_formdata(self, valuelist)


def noneFilter(value):
    """Filters empty strings into null values. Used for non-required fields
       like relbranches where "None" means "use the default"."""
    if not value:
        value = None
    return value


def truncateFilter(max_):
    """A filter that truncates the value to `max_' length
       if its initial length exceeds `max_'"""
    def filter(value):
        if len(value) > max_:
            return value[:max_]
        return value
    return filter


def collapseSpaces(value):
    """A filter that collapses spaces within a string. Used for the "partials"
       field to make the formatting slightly less strict."""
    # It's not clear to me why, but this filter sometimes gets passed empty
    # None rather than a string. The tests confirm that the filter is working
    # though...
    if value:
        value = value.replace(' ', '')
    return value


class ReleasesForm(Form):
    readyReleases = MultiCheckboxField('readyReleases')
    deleteReleases = MultiCheckboxField('deleteReleases')
    comment = TextAreaField('Extra information to release-drivers:')

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
    # If the client sends us a really long status we'd rather truncate
    # it than complain, because it's purely informational.
    # Use the Column length directly rather than duplicating its value.
    status = StringField('status', filters=[truncateFilter(Release.status.type.length)])

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


class ReleaseForm(Form):
    version = StringField('Version:', validators=[Regexp(ANY_VERSION_REGEX, message='Invalid version format.')])
    buildNumber = IntegerField('Build Number:', validators=[DataRequired('Build number is required.')])
    branch = StringField('Branch:', validators=[DataRequired('Branch is required')])
    mozillaRevision = StringField('Mozilla Revision:')
    dashboardCheck = BooleanField('Dashboard check?', default=False)
    mozillaRelbranch = StringField('Mozilla Relbranch:', filters=[noneFilter])
    comment = TextAreaField('Extra information to release-drivers:')

    def __init__(self, suggest=True, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if suggest:
            self.addSuggestions()

    def validate(self, *args, **kwargs):
        valid = Form.validate(self, *args, **kwargs)
        # If a relbranch has been passed revision is ignored.
        if self.mozillaRelbranch.data:
            self.mozillaRevision.data = self.mozillaRelbranch.data
        # However, if a relbranch hasn't been passed, revision is required.
        else:
            if not self.mozillaRevision.data:
                valid = False
                self.errors['mozillaRevision'] = ['Mozilla revision is required']

        return valid

    def addSuggestions(self):
        table = getReleaseTable(self.product.data)
        recentReleases = table.getRecent()

        # Before we make any suggestions we need to do some preprocessing of
        # the data to get it into useful structures. Specifically, we need a
        # set containing all of the recent versions, and a dict that associates
        # them with the branch they were built on.
        recentVersions = set()
        recentBranches = defaultdict(list)
        for release in recentReleases:
            recentVersions.add(release.version)
            recentBranches[release.branch].append(LooseVersion(release.version))

        # Now that we have the data in the format we want it in we can start
        # making suggestions.
        suggestedVersions = set()
        buildNumbers = {}

        # This wrapper method is used to centralize the build number suggestion
        # logic in one place, because there's more than one spot below that
        # adds a version suggestion.
        def addVersionSuggestion(version):
            suggestedVersions.add(version)
            # We want the UI to be able to automatically set build number
            # to the next available one for whatever version is entered.
            # To make this work we need to tell it what the next available
            # one is for all existing versions. We don't need to add versions
            # that are on build1, because it uses that as the default.
            maxBuildNumber = table.getMaxBuildNumber(version)
            if maxBuildNumber:
                buildNumbers[version] = maxBuildNumber + 1
            else:
                buildNumbers[version] = 1

        # Every version we see will have its potential next versions
        # suggested, except if we already have that version.
        # Note that we don't look through the entire table for every
        # version (because that could be expensive) but any versions
        # which are suggested and have already happened should be in
        # 'recentVersions', so it's unlikely we'll be suggesting
        # something that has already happened.
        for version in recentVersions:
            for v in getPossibleNextVersions(version):
                if v not in recentVersions:
                    addVersionSuggestion(v)

        # Additional, we need to suggest the most recent version for each
        # branch, because we may want a build2 (or higher) of it.
        for branchVersions in recentBranches.values():
            addVersionSuggestion(str(max(branchVersions)))

        # Finally, attach the suggestions to their fields.
        self.branch.suggestions = json.dumps(list(recentBranches.keys()))
        self.version.suggestions = json.dumps(list(suggestedVersions))
        self.buildNumber.suggestions = json.dumps(buildNumbers)

class FennecReleaseForm(ReleaseForm):
    product = HiddenField('product')
    l10nChangesets = JSONField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='fennec', product='fennec', *args, **kwargs)

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        # Revision is a disabled field if relbranch is present, so we shouldn't
        # put any data in it.
        if not row.mozillaRelbranch:
            self.mozillaRevision.data = row.mozillaRevision
        self.dashboardCheck.data = row.dashboardCheck
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch


class DesktopReleaseForm(ReleaseForm):
    partials = StringField('Partial versions:',
        validators=[Regexp(PARTIAL_VERSIONS_REGEX, message='Invalid partials format.')],
        filters=[collapseSpaces],
    )
    promptWaitTime = NullableIntegerField('Update prompt wait time:')
    l10nChangesets = PlainChangesetsField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def addSuggestions(self):
        ReleaseForm.addSuggestions(self)
        table = getReleaseTable(self.product.data)
        recentReleases = table.getRecent()
        seenVersions = []
        partials = {}
        # The UI will suggest any versions which are on the same branch as
        # the one given, but only the highest build number for that version.
        for release in reversed(recentReleases):
            if release.branch not in partials:
                partials[release.branch] = []
            if release.version not in seenVersions:
                partials[release.branch].append('%sbuild%d' % (release.version, release.buildNumber))
                seenVersions.append(release.version)
        self.partials.suggestions = json.dumps(partials)


class FirefoxReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='firefox', product='firefox', *args, **kwargs)

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        if not row.mozillaRelbranch:
            self.mozillaRevision.data = row.mozillaRevision
        self.partials.data = row.partials
        self.promptWaitTime.data = row.promptWaitTime
        self.dashboardCheck.data = row.dashboardCheck
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch
        self.comment.data = row.comment


class ThunderbirdReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')
    commRevision = StringField('Comm Revision:')
    commRelbranch = StringField('Comm Relbranch:', filters=[noneFilter])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='thunderbird', product='thunderbird', *args, **kwargs)

    def validate(self, *args, **kwargs):
        valid = DesktopReleaseForm.validate(self, *args, **kwargs)
        if self.commRelbranch.data:
            self.commRevision.data = self.commRelbranch.data
        else:
            if not self.commRevision.data:
                valid = False
                self.errors['commRevision'] = ['Comm revision is required']

        return valid

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        if not row.mozillaRelbranch:
            self.mozillaRevision.data = row.mozillaRevision
        if not row.commRelbranch:
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


class ReleaseEventsAPIForm(Form):
    sent = DateTimeField('Sent:', validators=[InputRequired('Sent is required.')])
    event_name = StringField('Event Name:', validators=[InputRequired('Event Name is required.'), Length(0, 150)])
    platform = StringField('Platform:')
    results = IntegerField('Results:', default=0, validators=[InputRequired('Results is required.')])
    chunkNum = IntegerField('Chunk Number:', default=1, validators=[InputRequired('Chunk Num is required.')])
    chunkTotal = IntegerField('Chunk Total:', default=1, validators=[InputRequired('Chunk Total is required.')])
    group = StringField('Group:', default='other')

    def validate(self, releaseName, *args, **kwargs):
        valid = Form.validate(self, *args, **kwargs)

        # Verify releaseName
        if len(releaseName) < 1 or len(releaseName) > 100:
            valid = False
            if 'releaseName' not in self.errors:
                self.errors['releaseName'] = []
            self.errors['releaseName'].append('Release name too short or too long. Must be greater than 0 and less than 100.')
        match = NAME_REGEX.match(releaseName)
        if not match:
            valid = False
            if 'releaseName' not in self.errors:
                self.errors['releaseName'] = []
            self.errors['releaseName'].append('Incorrect release name format.')
        else:
            start, end = match.span()
            if not releaseName[start:end] == releaseName:
                valid = False
                if 'releaseName' not in self.errors:
                    self.errors['releaseName'] = []
                self.errors['releaseName'].append('Incorrect release name format.')

        return valid
