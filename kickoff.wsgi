from ConfigParser import RawConfigParser
import logging
from os import path
import site

mydir = path.dirname(path.abspath(__file__))
site.addsitedir(mydir)
site.addsitedir(path.join(mydir, 'vendor/lib/python'))

from kickoff import db, app as application

cfg = RawConfigParser()
cfg.read(path.join(mydir, 'kickoff.ini'))
dburi = cfg.get('database', 'dburi')
logfile = cfg.get('logging', 'logfile')
loglevel = cfg.get('logging', 'level')
secretKey = cfg.get('app', 'secret_key')

logging.basicConfig(filename=logfile, level=loglevel, format='%(asctime)s - %(name)s.%(funcName)s#%(lineno)s: %(message)s')
application.config['SQLALCHEMY_DATABASE_URI'] = dburi
application.config['SQLALCHEMY_POOL_RECYCLE'] = 60
application.config['SECRET_KEY'] = secretKey
with application.test_request_context():
    db.init_app(application)
