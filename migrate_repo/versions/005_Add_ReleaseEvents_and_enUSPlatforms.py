from sqlalchemy import Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

import pytz

Base = declarative_base()


class ReleaseEvents(Base):
    __tablename__ = 'release_events'
    name = Column(String(100), nullable=False, primary_key=True)
    sent = Column(DateTime(pytz.utc), nullable=False)
    event_name = Column(String(500), nullable=False, primary_key=True)
    platform = Column(String(500), nullable=True)
    results = Column(Integer(), nullable=False)
    chunkNum = Column(Integer(), default=0, nullable=False)
    chunkTotal = Column(Integer(), default=0, nullable=False)


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)
    metadata = MetaData(bind=migrate_engine)

    def add_enUSPlatforms(table):
        enUSPlatforms = Column('enUSPlatforms', String(500), default=None,
                               nullable=True)
        enUSPlatforms.create(table)
    add_enUSPlatforms(Table('fennec_release', metadata, autoload=True))
    add_enUSPlatforms(Table('firefox_release', metadata, autoload=True))
    add_enUSPlatforms(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.enUSPlatforms.drop()
    Table('firefox_release', metadata, autoload=True).c.enUSPlatforms.drop()
    Table('thunderbird_release', metadata,
          autoload=True).c.enUSPlatforms.drop()
    Table('release_events', metadata, autoload=True).drop()
