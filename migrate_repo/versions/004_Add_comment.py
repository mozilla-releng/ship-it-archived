# Upgrade/downgrade the database with the comment field.
# CF bug #847505 for more information

from sqlalchemy import Column, MetaData, Table, Text


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    def add_comment(table):
        comment = Column('comment', Text, default=None)
        comment.create(table)
    add_comment(Table('fennec_release', metadata, autoload=True))
    add_comment(Table('firefox_release', metadata, autoload=True))
    add_comment(Table('thunderbird_release', metadata, autoload=True))


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    Table('fennec_release', metadata, autoload=True).c.comment.drop()
    Table('firefox_release', metadata, autoload=True).c.comment.drop()
    Table('thunderbird_release', metadata, autoload=True).c.comment.drop()
