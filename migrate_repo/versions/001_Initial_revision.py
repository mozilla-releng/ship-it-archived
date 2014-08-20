from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Release(object):
    name = Column(String(100), primary_key=True)
    submitter = Column(String(250), nullable=False)
    version = Column(String(10), nullable=False)
    buildNumber = Column(Integer(), nullable=False)
    branch = Column(String(50), nullable=False)
    mozillaRevision = Column(String(100), nullable=False)
    l10nChangesets = Column(Text(), nullable=False)
    dashboardCheck = Column(Boolean(), nullable=False, default=True)
    ready = Column(Boolean(), nullable=False, default=False)
    complete = Column(Boolean(), nullable=False, default=False)
    status = Column(String(250), default="")


class FennecRelease(Release, Base):
    __tablename__ = 'fennec_release'


class DesktopRelease(Release):
    partials = Column(String(100))


class FirefoxRelease(DesktopRelease, Base):
    __tablename__ = 'firefox_release'


class ThunderbirdRelease(DesktopRelease, Base):
    __tablename__ = 'thunderbird_release'
    commRevision = Column(String(100))


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)


def downgrade(migrate_engine):
    Base.drop_all(migrate_engine)
