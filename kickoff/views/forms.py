import logging
import simplejson as json
import re

from datetime import datetime
from ast import literal_eval
from collections import defaultdict

from flask.ext.wtf import (SelectMultipleField, ListWidget, CheckboxInput,
                           Form, BooleanField, StringField, TextAreaField,
                           DataRequired, IntegerField, HiddenField, Regexp,
                           DateTimeField, validators, DateField,
                           ValidationError)

from mozilla.build.versions import ANY_VERSION_REGEX, getPossibleNextVersions
from mozilla.release.l10n import parsePlainL10nChangesets

from kickoff.model import Release, getReleaseTable, getReleases
from kickoff.utils import parse_iso8601_to_date_time
from kickoff.versions import MozVersion

log = logging.getLogger(__name__)


PARTIAL_VERSIONS_REGEX = ('^(%sbuild\d+)(,%sbuild\d)*$' % (ANY_VERSION_REGEX, ANY_VERSION_REGEX))


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
            except ValueError as e:
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
        if value and len(value) > max_:
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


class OptionalPartials(object):
    """
    Allows empty partials if there is no recent releases.

    Works only for forms with form.recentReleases defined.
    """

    def __call__(self, form, field):
        try:
            log.debug("form.recentReleases: %s", form.recentReleases)
            if not field.data and not form.recentReleases:
                field.errors[:] = []
                raise validators.StopValidation()
        except AttributeError:
            pass


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
    shippedAt = DateTimeField('shippedAt', [validators.optional()])
    description = TextAreaField('description', [validators.optional()])
    isSecurityDriven = BooleanField('isSecurityDriven', [validators.optional()])
    release_eta = DateTimeField('release_eta', [validators.optional()])

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

            if self.description.data:
                # We just want to update the description & isSecurityDriven
                valid = True
            else:
                # Check if there is an other product-version already shipped
                similar = getReleases(
                    shipped=True, productFilter=release.product,
                    versionFilter=release.version)
                if similar and self.status.data != "Started":
                    # In most of the cases, it is useless since bug 1121032 has been implemented but keeping it
                    # in case we change/revert in the future and because we cannot always trust the client
                    valid = False
                    if 'shipped' not in self.errors:
                        self.errors['shipped'] = []
                    self.errors['shipped'].append('Version ' + release.version + ' already marked as shipped')

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
    mozillaRelbranch = StringField('Mozilla Relbranch:', filters=[noneFilter])
    comment = TextAreaField('Extra information to release-drivers:')
    description = TextAreaField('Description:')
    isSecurityDriven = BooleanField('Is a security driven release?', default=False)
    mh_changeset = StringField('Mozharness Revision:')
    release_eta_date = DateField('Release ETA date:', format='%Y-%m-%d',
                                 validators=[validators.optional()])
    release_eta_time = StringField('Release ETA time:')

    VALID_VERSION_PATTERN = re.compile(r"""^(\d+)\.(    # Major version number
        (0)(a1|a2|b(\d+)|esr)?    # 2-digit-versions (like 46.0, 46.0b1, 46.0esr)
        |(  # Here begins the 3-digit-versions.
            ([1-9]\d*)\.(\d+)|(\d+)\.([1-9]\d*) # 46.0.0 is not correct
        )(esr)? # Neither is 46.2.0b1
    )(build(\d+))?$""", re.VERBOSE)    # See more examples of (in)valid versions in the tests

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

        if self.VALID_VERSION_PATTERN.match(self.version.data) is None:
            valid = False
            self.errors['version'] = ['Version must match either X.0 or X.Y.Z']

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
            recentBranches[release.branch].append(MozVersion(release.version))

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

    def updateFromRow(self, row):
        self.version.data = row.version
        self.buildNumber.data = row.buildNumber
        self.branch.data = row.branch
        # Revision is a disabled field if relbranch is present, so we shouldn't
        # put any data in it.
        if not row.mozillaRelbranch:
            self.mozillaRevision.data = row.mozillaRevision
        self.l10nChangesets.data = row.l10nChangesets
        self.mozillaRelbranch.data = row.mozillaRelbranch
        self.mh_changeset.data = row.mh_changeset

        if row.release_eta:
            release_eta = parse_iso8601_to_date_time(row.release_eta)
            self.release_eta_date.data = release_eta.date()
            # Conversion needed because release_eta_time is a StringField
            self.release_eta_time.data = release_eta.strftime('%H:%M %Z')

    @property
    def release_eta(self):
        if self.release_eta_date.data and self.release_eta_time.data:
            dt = self.release_eta_date.data
            tm = datetime.strptime(self.release_eta_time.data,
                                   '%H:%M %Z').time()
            return datetime.combine(dt, tm)
        else:
            return None


class FennecReleaseForm(ReleaseForm):
    product = HiddenField('product')
    l10nChangesets = JSONField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='fennec', product='fennec', *args, **kwargs)


class DesktopReleaseForm(ReleaseForm):
    partials = StringField('Partial versions:',
                           validators=[OptionalPartials(), Regexp(PARTIAL_VERSIONS_REGEX, message='Invalid partials format.')],
                           filters=[collapseSpaces],
                           )
    promptWaitTime = NullableIntegerField('Update prompt wait time:')
    l10nChangesets = PlainChangesetsField('L10n Changesets:', validators=[DataRequired('L10n Changesets are required.')])

    def addSuggestions(self):
        ReleaseForm.addSuggestions(self)
        table = getReleaseTable(self.product.data)
        self.recentReleases = table.getRecentShipped()
        seenVersions = []
        partials = defaultdict(list)
        # The UI will suggest any versions which are on the same branch as
        # the one given, but only the highest build number for that version.
        # One exception is Firefox RC builds (version X.0), which should be added
        # to the list of betas
        for release in reversed(self.recentReleases):
            if release.version not in seenVersions:
                partials[release.branch].append('%sbuild%d' % (release.version, release.buildNumber))
                seenVersions.append(release.version)
                # here's the exception
                if release.product == 'firefox' and \
                   release.branch == 'releases/mozilla-release' and \
                   re.match('^\d+\.0$', release.version):
                    partials['releases/mozilla-beta'].append('%sbuild%d' % (release.version, release.buildNumber))
        self.partials.suggestions = json.dumps(partials)

    def updateFromRow(self, row):
        ReleaseForm.updateFromRow(self, row)
        self.partials.data = row.partials


class FirefoxReleaseForm(DesktopReleaseForm):
    product = HiddenField('product')

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='firefox', product='firefox', *args, **kwargs)

    def updateFromRow(self, row):
        DesktopReleaseForm.updateFromRow(self, row)
        self.comment.data = row.comment
        self.description.data = row.description


class DeveditionReleaseForm(FirefoxReleaseForm):

    def __init__(self, *args, **kwargs):
        ReleaseForm.__init__(self, prefix='devedition', product='devedition',
                             *args, **kwargs)


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
        DesktopReleaseForm.updateFromRow(self, row)
        self.promptWaitTime.data = row.promptWaitTime
        self.commRelbranch.data = row.commRelbranch
        if not row.commRelbranch:
            self.commRevision.data = row.commRevision


def getReleaseForm(release):
    """Helper method to figure out which form is needed for a release, based
       on its name."""
    release = release.lower()
    if release.startswith('fennec'):
        return FennecReleaseForm
    elif release.startswith('firefox'):
        return FirefoxReleaseForm
    elif release.startswith('devedition'):
        return DeveditionReleaseForm
    elif release.startswith('thunderbird'):
        return ThunderbirdReleaseForm
    else:
        raise ValueError("Can't find release table for release %s" % release)


class EditReleaseForm(Form):
    shippedAtDate = DateField('Shipped date', format='%Y/%m/%d', validators=[validators.optional(), ])
    shippedAtTime = StringField('Shipped time')
    isSecurityDriven = BooleanField('Is Security Driven ?')
    description = TextAreaField('Description')
    isShipped = BooleanField('Is Shipped ?')

    def validate_isShipped(form, field):
        if form.isShipped.data:
            dt = form.shippedAt

            if (not dt) or (dt > datetime.now()):
                raise ValidationError('Invalid Date for Shipped release')

    @property
    def shippedAt(self):
        dateAndTime = None

        if self.shippedAtDate.data:
            dt = self.shippedAtDate.data
            tm = datetime.strptime(self.shippedAtTime.data, '%H:%M:%S').time()
            dateAndTime = datetime.combine(dt, tm)

        return dateAndTime
