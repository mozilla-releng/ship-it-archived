from datetime import datetime, timedelta

import pytz

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from mozilla.release.info import getReleaseName

from kickoff import db

class Release(object):
    """A base class with all of the common columns for any release."""
    name = db.Column(db.String(100), primary_key=True)
    submitter = db.Column(db.String(250), nullable=False)
    _submittedAt = db.Column('submittedAt', db.DateTime(pytz.utc), nullable=False, default=datetime.utcnow)
    version = db.Column(db.String(10), nullable=False)
    buildNumber = db.Column(db.Integer(), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    mozillaRevision = db.Column(db.String(100), nullable=False)
    l10nChangesets = db.Column(db.Text(), nullable=False)
    dashboardCheck = db.Column(db.Boolean(), nullable=False, default=True)
    ready = db.Column(db.Boolean(), nullable=False, default=False)
    complete = db.Column(db.Boolean(), nullable=False, default=False)
    status = db.Column(db.String(250), default="")
    mozillaRelbranch = db.Column(db.String(50), default=None, nullable=True)

    # Dates are always returned in UTC time and ISO8601 format to make them
    # as transportable as possible.
    @hybrid_property
    def submittedAt(self):
        return pytz.utc.localize(self._submittedAt).isoformat()

    @submittedAt.setter
    def submittedAt(self, submittedAt):
        self._submittedAt = submittedAt

    def __init__(self, submitter, version, buildNumber, branch,
                 mozillaRevision, l10nChangesets, dashboardCheck,
                 mozillaRelbranch, submittedAt=None):
        self.name = getReleaseName(self.product, version, buildNumber)
        self.submitter = submitter
        self.version = version
        self.buildNumber = buildNumber
        self.branch = branch
        self.mozillaRevision = mozillaRevision
        self.l10nChangesets = l10nChangesets
        self.dashboardCheck = dashboardCheck
        self.mozillaRelbranch = mozillaRelbranch
        if submittedAt:
            self.submittedAt = submittedAt

    def toDict(self):
        me = {'product': self.product}
        for c in self.__table__.columns:
            me[c.name] = getattr(self, c.name)
        me['submittedAt'] = me['submittedAt']
        return me

    @classmethod
    def createFromForm(cls, form):
        raise NotImplementedError

    def updateFromForm(self, form):
        self.version = form.version.data
        self.buildNumber = form.buildNumber.data
        self.branch = form.branch.data
        self.mozillaRevision = form.mozillaRevision.data
        self.l10nChangesets = form.l10nChangesets.data
        self.dashboardCheck = form.dashboardCheck.data
        self.mozillaRelbranch = form.mozillaRelbranch.data
        self.name = getReleaseName(self.product, self.version, self.buildNumber)

    @classmethod
    def getRecent(cls, age=timedelta(weeks=7)):
        """Returns all releases of 'age' or newer."""
        since = datetime.now() - age
        return cls.query.filter(cls._submittedAt > since).all()

    @classmethod
    def getMaxBuildNumber(cls, version):
        """Returns the highest build number known for the version provided."""
        return cls.query \
            .with_entities(func.max(cls.buildNumber)) \
            .filter_by(version=version) \
            .one()[0]

    def __repr__(self):
        return '<Release %r>' % self.name

class FennecRelease(Release, db.Model):
    __tablename__ = 'fennec_release'
    product = 'fennec'

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(submitter, form.version.data,
                   form.buildNumber.data, form.branch.data,
                   form.mozillaRevision.data, form.l10nChangesets.data,
                   form.dashboardCheck.data, form.mozillaRelbranch.data)

class DesktopRelease(Release):
    partials = db.Column(db.String(100))
    promptWaitTime = db.Column(db.Integer(), nullable=True)

    def __init__(self, partials, promptWaitTime, *args, **kwargs):
        self.partials = partials
        self.promptWaitTime = promptWaitTime
        Release.__init__(self, *args, **kwargs)

    def updateFromForm(self, form):
        Release.updateFromForm(self, form)
        self.partials = form.partials.data
        self.promptWaitTime = form.promptWaitTime.data

class FirefoxRelease(DesktopRelease, db.Model):
    __tablename__ = 'firefox_release'
    product = 'firefox'

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(form.partials.data, form.promptWaitTime.data, submitter,
                   form.version.data, form.buildNumber.data, form.branch.data,
                   form.mozillaRevision.data, form.l10nChangesets.data,
                   form.dashboardCheck.data, form.mozillaRelbranch.data)

class ThunderbirdRelease(DesktopRelease, db.Model):
    __tablename__ = 'thunderbird_release'
    product = 'thunderbird'
    commRevision = db.Column(db.String(100))
    commRelbranch = db.Column(db.String(50))

    def __init__(self, commRevision, commRelbranch, *args, **kwargs):
        self.commRevision = commRevision
        self.commRelbranch = commRelbranch
        DesktopRelease.__init__(self, *args, **kwargs)

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(form.commRevision.data, form.commRelbranch.data,
                   form.partials.data, form.promptWaitTime.data, submitter,
                   form.version.data, form.buildNumber.data, form.branch.data,
                   form.mozillaRevision.data, form.l10nChangesets.data,
                   form.dashboardCheck.data, form.mozillaRelbranch.data)

    def updateFromForm(self, form):
        DesktopRelease.updateFromForm(self, form)
        self.commRevision = form.commRevision.data
        self.commRelbranch = form.commRelbranch.data

def getReleaseTable(release):
    """Helper method to figure out what type of release a request is for.
       Because the API methods are not specific to the type of release, we
       need this to make sure we operate on the correct table."""
    release = release.lower()
    if release.startswith('fennec'):
        return FennecRelease
    elif release.startswith('firefox'):
        return FirefoxRelease
    elif release.startswith('thunderbird'):
        return ThunderbirdRelease
    else:
        raise ValueError("Can't find release table for release %s" % release)

def getReleases(ready=None, complete=None):
    filters = {}
    if ready is not None:
        filters['ready'] = ready
    if complete is not None:
        filters['complete'] = complete
    releases = []
    for table in (FennecRelease, FirefoxRelease, ThunderbirdRelease):
        if filters:
            for r in table.query.filter_by(**filters):
                releases.append(r)
        else:
            for r in table.query.all():
                releases.append(r)
    return releases
