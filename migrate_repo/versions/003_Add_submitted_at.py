from sqlalchemy import Column, MetaData, Table, DateTime

import pytz

from datetime import datetime

def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    def add_submittedAt(table):
        submittedAt = Column('submittedAt', DateTime(pytz.utc), default=datetime.utcnow)
        submittedAt.create(table)
    add_submittedAt(Table('fennec_release', metadata, autoload=True))
    add_submittedAt(Table('firefox_release', metadata, autoload=True))
    add_submittedAt(Table('thunderbird_release', metadata, autoload=True))

def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.submittedAt.drop()
    Table('firefox_release', metadata, autoload=True).c.submittedAt.drop()
    Table('thunderbird_release', metadata, autoload=True).c.submittedAt.drop()
