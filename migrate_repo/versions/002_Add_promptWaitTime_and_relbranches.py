from sqlalchemy import Column, String, Integer, MetaData, Table

def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    fennec = Table('fennec_release', metadata, autoload=True)
    firefox = Table('firefox_release', metadata, autoload=True)
    thunderbird = Table('thunderbird_release', metadata, autoload=True)
    def addMozillaRelbranch(table):
        mozillaRelbranch = Column('mozillaRelbranch', String(50), default=None, nullable=True)
        mozillaRelbranch.create(table)
    addMozillaRelbranch(fennec)
    addMozillaRelbranch(firefox)
    addMozillaRelbranch(thunderbird)
    def addPromptWaitTime(table):
        promptWaitTime = Column('promptWaitTime', Integer(), nullable=True)
        promptWaitTime.create(table)
    addPromptWaitTime(firefox)
    addPromptWaitTime(thunderbird)
    commRelbranch = Column('commRelbranch', String(50), default=None, nullable=True)
    commRelbranch.create(thunderbird)

def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    fennec = Table('fennec_release', metadata, autoload=True)
    firefox = Table('firefox_release', metadata, autoload=True)
    thunderbird = Table('thunderbird_release', metadata, autoload=True)
    for t in (fennec, firefox, thunderbird):
        t.c.mozillaRelbranch.drop()
    for t in (firefox, thunderbird):
        t.c.promptWaitTime.drop()
    thunderbird.c.commRelbranch.drop()
