# Upgrade/downgrade the database with the shippedAt field.
# CF bug #1101596 for more information
from sqlalchemy import Column, MetaData, Table, String


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_mh_changeset(table):
        mh_changeset = Column('mh_changeset', String(100), nullable=True)
        mh_changeset.create(table)

    add_mh_changeset(Table('fennec_release', metadata, autoload=True))
    add_mh_changeset(Table('firefox_release', metadata, autoload=True))
    add_mh_changeset(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.mh_changeset.drop()
    Table('firefox_release', metadata, autoload=True).c.mh_changeset.drop()
    Table('thunderbird_release', metadata, autoload=True).c.mh_changeset.drop()
