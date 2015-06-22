from datetime import datetime, timedelta

import pytz
import json
import re

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

from mozilla.release.info import getReleaseName

from kickoff import db


class Release(object):

    """A base class with all of the common columns for any release."""
    name = db.Column(db.String(100), primary_key=True)
    submitter = db.Column(db.String(250), nullable=False)
    _submittedAt = db.Column('submittedAt', db.DateTime(pytz.utc),
                             nullable=False, default=datetime.utcnow)
    _shippedAt = db.Column('shippedAt', db.DateTime(pytz.utc))
    version = db.Column(db.String(10), nullable=False)
    buildNumber = db.Column(db.Integer(), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    mozillaRevision = db.Column(db.String(100), nullable=False)
    l10nChangesets = db.Column(db.Text(), nullable=False)
    dashboardCheck = db.Column(db.Boolean(), nullable=False, default=False)
    ready = db.Column(db.Boolean(), nullable=False, default=False)
    complete = db.Column(db.Boolean(), nullable=False, default=False)
    status = db.Column(db.String(250), default="")
    mozillaRelbranch = db.Column(db.String(50), default=None, nullable=True)
    enUSPlatforms = db.Column(db.String(500), default=None, nullable=True)
    comment = db.Column(db.Text, default=None, nullable=True)
    starter = db.Column(db.String(250), nullable=True)

    # Dates are always returned in UTC time and ISO8601 format to make them
    # as transportable as possible.
    @hybrid_property
    def submittedAt(self):
        return pytz.utc.localize(self._submittedAt).isoformat()

    @submittedAt.setter
    def submittedAt(self, submittedAt):
        self._submittedAt = submittedAt

    # Dates are always returned in UTC time and ISO8601 format to make them
    # as transportable as possible.
    @hybrid_property
    def shippedAt(self):
        if self._shippedAt:
            return pytz.utc.localize(self._shippedAt).isoformat()
        else:
            # Not (yet) shipped releaes
            return None

    @shippedAt.setter
    def shippedAt(self, shippedAt):
        self._shippedAt = shippedAt

    def __init__(self, submitter, version, buildNumber, branch,
                 mozillaRevision, l10nChangesets, dashboardCheck,
                 mozillaRelbranch, enUSPlatforms=None, submittedAt=None,
                 shippedAt=None, comment=None):
        self.name = getReleaseName(self.product, version, buildNumber)
        self.submitter = submitter
        self.version = version.strip()
        self.buildNumber = buildNumber
        self.branch = branch.strip()
        self.mozillaRevision = mozillaRevision.strip()
        self.l10nChangesets = l10nChangesets
        self.dashboardCheck = dashboardCheck
        self.mozillaRelbranch = mozillaRelbranch
        self.enUSPlatforms = enUSPlatforms
        if submittedAt:
            self.submittedAt = submittedAt
        if shippedAt:
            self.shippedAt = shippedAt
        if comment:
            self.comment = comment

    def toDict(self):
        me = {'product': self.product}
        for c in self.__table__.columns:
            me[c.name] = getattr(self, c.name)
        me['submittedAt'] = me['submittedAt']
        me['shippedAt'] = me['shippedAt']
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
        self.name = getReleaseName(self.product, self.version,
                                   self.buildNumber)
        self.comment = form.comment.data

    @classmethod
    def getRecent(cls, age=timedelta(weeks=7)):
        """Returns all releases of 'age' or newer."""
        since = datetime.now() - age
        return cls.query.filter(cls._submittedAt > since).all()

    @classmethod
    def getRecentShipped(cls, age=timedelta(weeks=40)):
        """Returns all shipped releases of 'age' or newer."""
        since = datetime.now() - age
        return [
            r for r in cls.query.filter(cls._submittedAt > since).all() if
            r.status == "postrelease" or
            ReleaseEvents.getCurrentStatus(r.name) == "postrelease"
        ]

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
                   form.dashboardCheck.data, form.mozillaRelbranch.data,
                   form.comment.data)


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
                   form.dashboardCheck.data, form.mozillaRelbranch.data,
                   form.comment.data)


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
                   form.dashboardCheck.data, form.mozillaRelbranch.data,
                   form.comment.data)

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


def getReleases(ready=None, complete=None, status=None, productFilter=None, versionFilter=None, versionFilterCategory=None, searchOtherShipped=False, lastRelease=None):
    filters = {}
    if ready is not None:
        filters['ready'] = ready
    if complete is not None:
        filters['complete'] = complete
    if status is not None:
        filters['status'] = status
    if versionFilter is not None:
        filters['version'] = versionFilter
    if productFilter:
        tables = (getReleaseTable(productFilter),)
    else:
        tables = (FennecRelease, FirefoxRelease, ThunderbirdRelease)
    releases = []
    for table in tables:
        if filters:
            if lastRelease:
                # Retrieve the last X version
                results = table.query.filter_by(**filters).order_by(table._submittedAt.desc()).limit(40)
            else:
                results = table.query.filter_by(**filters)
            for r in results:
                if not versionFilterCategory:
                    releases.append(r)
                else:
                    # We are using a manual filter here.
                    # we are not doing it through SQL because:
                    # * regexp queries are not really standard in SQL
                    # * sqlalchemy does not provide a wrapper for this
                    for versionFilter in versionFilterCategory:
                        if re.match(versionFilter, r.version):
                            releases.append(r)
        else:
            for r in table.query.all():
                releases.append(r)
    status_groups = {'tag': 'Tagging', 'build': 'Builds', 'repack': 'Repacks',
                     'update': 'Update', 'releasetest': 'Release Test',
                     'readyforrelease': 'Ready For Release',
                     'postrelease': 'Post Release'}
    for release in releases:
        status = ReleaseEvents.getCurrentStatus(release.name)
        if status:
            release.status = status_groups[status]

        if not searchOtherShipped:
            # Disable this search to avoid an infinite recursion

            # Search if we don't have a build (same version + product) already shipped
            similar = getReleases(status="postrelease", productFilter=release.product,
                                  versionFilter=release.version, searchOtherShipped=True)
            if similar:
                # The release has been marked as shipped (this build or an other)
                # Store this information to disable the button to avoid two builds of
                # the same version marked as shipped
                release.ReleaseMarkedAsShipped = True

    return releases


class ReleaseEvents(db.Model):

    """A base class to store release events primarily from buildbot."""
    __tablename__ = 'release_events'
    name = db.Column(db.String(100), nullable=False, primary_key=True)
    _sent = db.Column('sent', db.DateTime(pytz.utc), nullable=False)
    event_name = db.Column(db.String(150), nullable=False, primary_key=True)
    platform = db.Column(db.String(500), nullable=True)
    results = db.Column(db.Integer(), nullable=False)
    chunkNum = db.Column(db.Integer(), default=0, nullable=False)
    chunkTotal = db.Column(db.Integer(), default=0, nullable=False)
    group = db.Column(db.String(100), default=None, nullable=True)

    # Dates are always returned in UTC time and ISO8601 format to make them
    # as transportable as possible.
    @hybrid_property
    def sent(self):
        return pytz.utc.localize(self._sent).isoformat()

    @sent.setter
    def sent(self, sent):
        self._sent = sent

    def __init__(self, name, sent, event_name, platform, results, chunkNum=0,
                 chunkTotal=0, group=None):
        self.name = name
        if sent:
            self.sent = sent
        self.event_name = event_name
        self.platform = platform
        self.results = results
        self.chunkNum = chunkNum
        self.chunkTotal = chunkTotal
        self.group = group

    def toDict(self):
        me = {}
        for c in self.__table__.columns:
            me[c.name] = str(getattr(self, c.name))
        return me

    @classmethod
    def createFromForm(cls, releaseName, form):
        return cls(releaseName, form.sent.data, form.event_name.data,
                   form.platform.data, form.results.data, form.chunkNum.data,
                   form.chunkTotal.data, form.group.data)

    def __repr__(self):
        return '<ReleaseEvents %r>' % self.name

    @classmethod
    def getEvents(cls, group=None):
        filters = {}
        if group is not None:
            filters['group'] = group
        if filters:
            return cls.query.filter_by(**filters)
        else:
            return cls.query.all()

    @classmethod
    def getStatus(cls, name):
        if not cls.query.filter_by(name=name).first():
            return None
        status = {'tag': cls.tagStatus, 'build': cls.buildStatus, 'repack': cls.repackStatus,
                  'update': cls.updateStatus, 'releasetest': cls.releasetestStatus,
                  'readyforrelease': cls.readyForReleaseStatus, 'postrelease': cls.postreleaseStatus}
        for step in status:
            status[step] = status[step](name)
        status['name'] = name
        return status

    @classmethod
    def getCurrentStatus(cls, name):
        status = cls.getStatus(name)
        status_order = ['tag', 'build', 'repack', 'update', 'releasetest',
                        'readyforrelease', 'postrelease']

        currentStatus = None
        if status:
            for s in reversed(status_order):
                if status[s]['progress'] != 0:
                    return s

        return currentStatus

    @classmethod
    def tagStatus(cls, name):
        if cls.query.filter_by(name=name, group='tag').count() > 0:
            return {'progress': 1.00}
        return {'progress': 0.00}

    @classmethod
    def buildStatus(cls, name):
        build_events = cls.query.filter_by(name=name, group='build')

        builds = {'platforms': {}, 'progress': 0.00}
        for platform in cls.getEnUSPlatforms(name):
            builds['platforms'][platform] = 0.00

        for build in build_events:
            builds['platforms'][build.platform] = 1.00
            builds['progress'] += (1.00/len(builds['platforms']))

        return builds

    @classmethod
    def repackStatus(cls, name):
        repack_events = cls.query.filter_by(name=name, group='repack')

        repacks = {'platforms': {}, 'progress': 0.00}
        for platform in cls.getEnUSPlatforms(name):
            repacks['platforms'][platform] = 0.00

        for repack in repack_events:
            if repacks['platforms'][repack.platform] != 1:
                if 'complete' not in repack.event_name:
                    repacks['platforms'][repack.platform] += (1.00/repack.chunkTotal)
                else:
                    repacks['platforms'][repack.platform] = 1.00
        repacks['progress'] = (sum(repacks['platforms'].values()) / len(repacks['platforms']))

        for platform, progress in repacks['platforms'].items():
            repacks['platforms'][platform] = round(progress, 2)

        return repacks

    @classmethod
    def updateStatus(cls, name):
        if cls.query.filter_by(name=name, group='update').count() > 0:
            return {'progress': 1.00}
        return {'progress': 0.00}

    @classmethod
    def releasetestStatus(cls, name):
        if cls.query.filter_by(name=name, group='releasetest').count() > 0:
            return {'progress': 1.00}
        return {'progress': 0.00}

    @classmethod
    def readyForReleaseStatus(cls, name):
        update_verify_events = cls.query.filter_by(name=name, group='update_verify')
        release_events = cls.query.filter_by(name=name, group='release')

        update_verifys = {}
        for platform in cls.getEnUSPlatforms(name):
            update_verifys[platform] = 0.00

        for update_verify in update_verify_events:
            if update_verifys[update_verify.platform] != 1:
                if 'complete' not in update_verify.event_name:
                    update_verifys[update_verify.platform] += (1.00/update_verify.chunkTotal)
                else:
                    update_verifys[update_verify.platform] = 1.00
        data = {'platforms': update_verifys, 'progress': 0.00}
        data['progress'] = (sum(data['platforms'].values()) / len(data['platforms']))

        for platform, progress in data['platforms'].items():
            data['platforms'][platform] = round(progress, 2)

        if release_events.first():
            data['progress'] = 1.00

        return data

    @classmethod
    def postreleaseStatus(cls, name):
        if cls.query.filter_by(name=name, group='postrelease').count() > 0:
            return {'progress': 1.00}
        return {'progress': 0.00}

    @classmethod
    def getEnUSPlatforms(cls, name):
        releaseTable = getReleaseTable(name.split('-')[0].title())
        release = releaseTable.query.filter_by(name=name).first()
        return json.loads(release.enUSPlatforms)
