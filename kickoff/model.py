from mozilla.release.info import getReleaseName

from kickoff import db

class Release(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    submitter = db.Column(db.String(250), nullable=False)
    product = db.Column(db.String(30), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    buildNumber = db.Column(db.Integer(), nullable=False)
    mozillaRevision = db.Column(db.String(100), nullable=False)
    commRevision = db.Column(db.String(100))
    l10nChangesets = db.Column(db.String(250), nullable=False)
    partials = db.Column(db.String(50), nullable=False)
    whatsnew = db.Column(db.Boolean(), nullable=False, default=False)
    complete = db.Column(db.Boolean(), nullable=False, default=False)

    def __init__(self, submitter, product, version, buildNumber,
                 mozillaRevision, l10nChangesets, partials, whatsnew,
                 commRevision=None):
        self.name = getReleaseName(product, version, buildNumber)
        self.submitter = submitter
        self.product = product
        self.version = version
        self.buildNumber = buildNumber
        self.mozillaRevision = mozillaRevision
        self.l10nChangesets = l10nChangesets
        self.partials = partials
        self.whatsnew = whatsnew
        if commRevision:
            self.commRevision = commRevision
    
    def toDict(self):
        me = {}
        for c in self.__table__.columns:
            me[c.name] = getattr(self, c.name)
        return me

    def __repr__(self):
        return '<Release %r>' % self.name
