from mozilla.release.info import getReleaseName

from kickoff import db

class Release(object):
    """A base class with all of the common columns for any release."""
    name = db.Column(db.String(100), primary_key=True)
    submitter = db.Column(db.String(250), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    buildNumber = db.Column(db.Integer(), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    mozillaRevision = db.Column(db.String(100), nullable=False)
    l10nChangesets = db.Column(db.Text(), nullable=False)
    dashboardCheck = db.Column(db.Boolean(), nullable=False, default=True)
    ready = db.Column(db.Boolean(), nullable=False, default=False)
    complete = db.Column(db.Boolean(), nullable=False, default=False)
    status = db.Column(db.String(250), default="")

    def __init__(self, submitter, version, buildNumber, branch,
                 mozillaRevision, l10nChangesets, dashboardCheck):
        self.name = getReleaseName(self.product, version, buildNumber)
        self.submitter = submitter
        self.version = version
        self.buildNumber = buildNumber
        self.branch = branch
        self.mozillaRevision = mozillaRevision
        self.l10nChangesets = l10nChangesets
        self.dashboardCheck = dashboardCheck
    
    def toDict(self):
        me = {'product': self.product}
        for c in self.__table__.columns:
            me[c.name] = getattr(self, c.name)
        return me

    @classmethod
    def createFromForm(self):
        raise NotImplementedError

    def __repr__(self):
        return '<Release %r>' % self.name

class FennecRelease(Release, db.Model):
    __tablename__ = 'fennec_release'
    product = 'fennec'

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(submitter, form.version.data,
            form.buildNumber.data, form.branch.data, form.mozillaRevision.data,
            form.l10nChangesets.data, form.dashboardCheck.data)

class DesktopRelease(Release):
    partials = db.Column(db.String(100))

    def __init__(self, partials, *args, **kwargs):
        self.partials = partials
        Release.__init__(self, *args, **kwargs)

class FirefoxRelease(DesktopRelease, db.Model):
    __tablename__ = 'firefox_release'
    product = 'firefox'

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(form.partials.data, submitter, form.version.data,
            form.buildNumber.data, form.branch.data, form.mozillaRevision.data,
            form.l10nChangesets.data, form.dashboardCheck.data)

class ThunderbirdRelease(DesktopRelease, db.Model):
    __tablename__ = 'thunderbird_release'
    product = 'thunderbird'
    commRevision = db.Column(db.String(100))

    def __init__(self, commRevision, *args, **kwargs):
        self.commRevision = commRevision
        DesktopRelease.__init__(self, *args, **kwargs)

    @classmethod
    def createFromForm(cls, submitter, form):
        return cls(form.commRevision.data, form.partials.data,
            submitter, form.version.data, form.buildNumber.data,
            form.branch.data, form.mozillaRevision.data,
            form.l10nChangesets.data, form.dashboardCheck.data)

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
