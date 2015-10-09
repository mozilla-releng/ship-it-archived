# Upgrade/downgrade the database with the shippedAt field.
# CF bug #1101596 for more information
from sqlalchemy import Column, MetaData, Table, Boolean, Text

import pytz

from datetime import datetime


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_isSecurityDriven(table):
        isSecurityDriven = Column('isSecurityDriven', Boolean())
        isSecurityDriven.create(table)
    add_isSecurityDriven(Table('fennec_release', metadata, autoload=True))
    add_isSecurityDriven(Table('firefox_release', metadata, autoload=True))
    add_isSecurityDriven(Table('thunderbird_release', metadata, autoload=True))

    def add_description(table):
        description = Column('description', Text, default=None)
        description.create(table)
    add_description(Table('fennec_release', metadata, autoload=True))
    add_description(Table('firefox_release', metadata, autoload=True))
    add_description(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.isSecurityDriven.drop()
    Table('firefox_release', metadata, autoload=True).c.isSecurityDriven.drop()
    Table('thunderbird_release', metadata, autoload=True).c.isSecurityDriven.drop()
    Table('fennec_release', metadata, autoload=True).c.description.drop()
    Table('firefox_release', metadata, autoload=True).c.description.drop()
    Table('thunderbird_release', metadata, autoload=True).c.description.drop()
