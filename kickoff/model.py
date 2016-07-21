from datetime import datetime, timedelta

import pytz
import re

from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import or_
from mozilla.release.info import getReleaseName

from kickoff import db, config


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
    comment = db.Column(db.Text, default=None, nullable=True)
    description = db.Column(db.Text, default=None, nullable=True)
    isSecurityDriven = db.Column(db.Boolean(), nullable=False, default=False)
    starter = db.Column(db.String(250), nullable=True)
    mh_changeset = db.Column(db.String(100), nullable=True)

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
                 mozillaRelbranch, submittedAt=None,
                 shippedAt=None, comment=None, description=None,
                 isSecurityDriven=False, mh_changeset=None):
        self.name = getReleaseName(self.product, version, buildNumber)
        self.submitter = submitter
        self.version = version.strip()
        self.buildNumber = buildNumber
        self.branch = branch.strip()
        self.mozillaRevision = mozillaRevision.strip()
        self.l10nChangesets = l10nChangesets
        self.dashboardCheck = dashboardCheck
        self.mozillaRelbranch = mozillaRelbranch
        if submittedAt:
            self.submittedAt = submittedAt
        if shippedAt:
            self.shippedAt = shippedAt
        if comment:
            self.comment = comment
        if description:
            self.description = description
        self.isSecurityDriven = isSecurityDriven
        self.mh_changeset = mh_changeset

    @property
    def isShippedWithL10n(self):
        return self._shippedAt and self.l10nChangesets != config.LEGACY_KEYWORD

    def toDict(self):
        me = {'product': self.product}
        for c in self.__table__.columns:
            me[c.name] = getattr(self, c.name)
        me['submittedAt'] = me['submittedAt']
        me['shippedAt'] = me['shippedAt']
        return me

    @classmethod
    def createFromForm(cls, *args, **kwargs):
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
        self.description = form.description.data
        self.isSecurityDriven = form.isSecurityDriven.data
        self.mh_changeset = form.mh_changeset.data

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
            r for r in cls.query.filter(cls._submittedAt > since).filter(cls._shippedAt != None).all()
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
        return cls(
            submitter=submitter,
            version=form.version.data,
            buildNumber=form.buildNumber.data,
            branch=form.branch.data,
            mozillaRevision=form.mozillaRevision.data,
            l10nChangesets=form.l10nChangesets.data,
            dashboardCheck=form.dashboardCheck.data,
            mozillaRelbranch=form.mozillaRelbranch.data,
            comment=form.comment.data,
            description=form.description.data,
            isSecurityDriven=form.isSecurityDriven.data,
            mh_changeset=form.mh_changeset.data)


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
        return cls(
            partials=form.partials.data,
            promptWaitTime=form.promptWaitTime.data,
            submitter=submitter,
            version=form.version.data,
            buildNumber=form.buildNumber.data,
            branch=form.branch.data,
            mozillaRevision=form.mozillaRevision.data,
            l10nChangesets=form.l10nChangesets.data,
            dashboardCheck=form.dashboardCheck.data,
            mozillaRelbranch=form.mozillaRelbranch.data,
            comment=form.comment.data,
            description=form.description.data,
            isSecurityDriven=form.isSecurityDriven.data,
            mh_changeset=form.mh_changeset.data)


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
        return cls(
            commRevision=form.commRevision.data,
            commRelbranch=form.commRelbranch.data,
            partials=form.partials.data,
            promptWaitTime=form.promptWaitTime.data,
            submitter=submitter,
            version=form.version.data,
            buildNumber=form.buildNumber.data,
            branch=form.branch.data,
            mozillaRevision=form.mozillaRevision.data,
            l10nChangesets=form.l10nChangesets.data,
            dashboardCheck=form.dashboardCheck.data,
            mozillaRelbranch=form.mozillaRelbranch.data,
            comment=form.comment.data,
            description=form.description.data,
            isSecurityDriven=form.isSecurityDriven.data,
            mh_changeset=form.mh_changeset.data)

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


class ReleasesPaginationCriteria:
    def __init__(self, start, length, orderByDict):
        self.start = start
        self.length = length
        self.orderByDict = orderByDict


def getReleases(ready=None, complete=None, shipped=None, productFilter=None,
                versionFilter=None, versionFilterCategory=None,
                searchOtherShipped=False, lastRelease=None,
                paginationCriteria=None, searchFilter=None):

    filters = {}
    if ready is not None:
        filters['ready'] = ready
    if complete is not None:
        filters['complete'] = complete
    if versionFilter is not None:
        filters['version'] = versionFilter

    if paginationCriteria:
        tables = (ProductReleasesView, )
    elif productFilter:
        tables = (getReleaseTable(productFilter),)
    else:
        tables = (FennecRelease, FirefoxRelease, ThunderbirdRelease)

    releases = []

    for table in tables:
        if filters:
            qry = table.query.filter_by(**filters)
            if shipped:
                qry = qry.filter(table._shippedAt != None)
            if lastRelease and not paginationCriteria:
                # Retrieve the last X version
                qry = qry.order_by(table._submittedAt.desc()).limit(40)
            else:
                if searchFilter:
                    searchList = table.getSearchList(searchFilter)
                    qry = qry.filter(or_(*searchList))

                if paginationCriteria:
                    if productFilter:
                        qry = qry.filter(ProductReleasesView.product.contains(productFilter))

                    orderByList = getOrderByList(table, paginationCriteria.orderByDict)

                    qry = qry.order_by(*orderByList).limit(paginationCriteria.length).offset(paginationCriteria.start)

            results = qry.all()

            for r in results:
                if not versionFilterCategory:
                    releases.append(r)
                else:
                    # We are using a manual filter here.
                    # we are not doing it through SQL because:
                    # * regexp queries are not really standard in SQL
                    # * sqlalchemy does not provide a wrapper for this
                    for versionFilter in versionFilterCategory:
                        if re.match(versionFilter[1], r.version):
                            r.category = versionFilter[0]
                            releases.append(r)
        else:
            if paginationCriteria:
                orderByList = getOrderByList(table, paginationCriteria.orderByDict)
                results = table.query.order_by(*orderByList).limit(paginationCriteria.length).offset(paginationCriteria.start).all()
            else:
                results = table.query.all()

            for r in results:
                releases.append(r)

    for release in releases:
        if not searchOtherShipped and not paginationCriteria:
            # Disable this search to avoid an infinite recursion

            # Search if we don't have a build (same version + product) already shipped
            similar = getReleases(shipped=True, productFilter=release.product,
                                  versionFilter=release.version,
                                  searchOtherShipped=True)
            if similar:
                # The release has been marked as shipped (this build or an other)
                # Store this information to disable the button to avoid two builds of
                # the same version marked as shipped
                release.ReleaseMarkedAsShipped = True

    return releases


def getOrderByList(obj, orderByDict={}):
    lst = []

    for k, v in orderByDict.iteritems():
        column = getattr(obj, k)
        direction = getattr(column, v)
        lst.append(direction())

    return lst


class ProductReleasesView(Release, db.Model):
    __tablename__ = 'product_releases'

    product = db.Column(db.String(100))
    partials = db.Column(db.String(100))
    promptWaitTime = db.Column(db.Integer(), nullable=True)
    commRevision = db.Column(db.String(100))
    commRelbranch = db.Column(db.String(50))

    @classmethod
    def OR(cls, searchList):
        return or_(*searchList)

    @classmethod
    def getSearchList(cls, searchDict={}):
        lst = []
        for k, v in searchDict.iteritems():
            column = getattr(cls, k)
            contains = getattr(column, 'contains')
            lst.append(contains(v))

        return lst
