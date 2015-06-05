# Upgrade/downgrade the database with the shippedAt field.
# CF bug #1101596 for more information
from sqlalchemy import Column, MetaData, Table, DateTime

import pytz

from datetime import datetime


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_shippedAt(table):
        shippedAt = Column('shippedAt', DateTime(pytz.utc))
        shippedAt.create(table)
    add_shippedAt(Table('fennec_release', metadata, autoload=True))
    add_shippedAt(Table('firefox_release', metadata, autoload=True))
    add_shippedAt(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.shippedAt.drop()
    Table('firefox_release', metadata, autoload=True).c.shippedAt.drop()
    Table('thunderbird_release', metadata, autoload=True).c.shippedAt.drop()
