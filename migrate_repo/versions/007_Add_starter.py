# Upgrade/downgrade the database with the starter field.
# CF bug #1074228 for more information

from sqlalchemy import Column, MetaData, Table, String


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_starter(table):
        starter = Column('starter', String(255), default=None)
        starter.create(table)
    add_starter(Table('fennec_release', metadata, autoload=True))
    add_starter(Table('firefox_release', metadata, autoload=True))
    add_starter(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.starter.drop()
    Table('firefox_release', metadata, autoload=True).c.starter.drop()
    Table('thunderbird_release', metadata, autoload=True).c.starter.drop()
