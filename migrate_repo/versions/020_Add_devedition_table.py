import pytz
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, MetaData, Table

meta = MetaData()
devedition = Table(
    'devedition_release', meta,
    Column('submittedAt', DateTime(pytz.utc), nullable=True,
           default=datetime.utcnow),
    Column('shippedAt', DateTime(pytz.utc)),
    Column('name', String(100), primary_key=True),
    Column('submitter', String(250), nullable=False),
    Column('version', String(10), nullable=False),
    Column('buildNumber', Integer(), nullable=False),
    Column('branch', String(50), nullable=False),
    Column('mozillaRevision', String(100), nullable=False),
    Column('l10nChangesets', Text(), nullable=False),
    Column('ready', Boolean(), nullable=False, default=False),
    Column('complete', Boolean(), nullable=False, default=False),
    Column('status', String(250), default=""),
    Column('mozillaRelbranch', String(50), default=None, nullable=True),
    Column('comment', Text, default=None, nullable=True),
    Column('description', Text, default=None, nullable=True),
    Column('isSecurityDriven', Boolean(), nullable=True, default=False),
    Column('starter', String(255), nullable=True),
    Column('mh_changeset', String(100), nullable=True),
    Column('partials', String(100)),
    Column('promptWaitTime', Integer(), nullable=True),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    devedition.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    devedition.drop()
