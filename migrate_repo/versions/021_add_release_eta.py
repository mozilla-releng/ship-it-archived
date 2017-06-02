from sqlalchemy import Column, MetaData, Table, DateTime
import pytz


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_release_eta(table):
        release_eta = Column('release_eta', DateTime(pytz.utc))
        release_eta.create(table)

    add_release_eta(Table('fennec_release', metadata, autoload=True))
    add_release_eta(Table('firefox_release', metadata, autoload=True))
    add_release_eta(Table('devedition_release', metadata, autoload=True))
    add_release_eta(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.release_eta.drop()
    Table('firefox_release', metadata, autoload=True).c.release_eta.drop()
    Table('devedition_release', metadata, autoload=True).c.release_eta.drop()
    Table('thunderbird_release', metadata, autoload=True).c.release_eta.drop()
