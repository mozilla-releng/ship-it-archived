# Upgrade/downgrade the database with the group field in the
# ReleaseEvents table.

from sqlalchemy import Column, MetaData, Table, String


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    table = Table('release_events', metadata, autoload=True)
    group = Column('group', String(100), default=None,
                   nullable=True)
    group.create(table)


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('release_events', metadata, autoload=True).c.group.drop()
