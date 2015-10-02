import logging
from os import path
import site

from paste.auth.basic import AuthBasicHandler

mydir = path.dirname(path.abspath(__file__))
site.addsitedir(mydir)
site.addsitedir(path.join(mydir, 'vendor/lib/python'))

from kickoff import app, db
from kickoff.log import cef_config

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-d", "--db", dest="db")
    parser.add_option("--host", dest="host")
    parser.add_option("--port", dest="port", type="int")
    parser.add_option("-l", "--logfile", dest="logfile")
    parser.add_option("-u", "--username", dest="username")
    parser.add_option("-p", "--password", dest="password")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true")
    parser.add_option("--cef-log", dest="cef_log", default="cef.log")
    options, args = parser.parse_args()

    log_level = logging.INFO
    if options.verbose:
        log_level = logging.DEBUG
    logging.basicConfig(filename=options.logfile, level=log_level)

    app.config['SQLALCHEMY_DATABASE_URI'] = options.db
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'NOT A SECRET'
    app.config.update(cef_config(options.cef_log))

    with app.test_request_context():
        db.init_app(app)
        db.create_all()

    def auth(environ, username, password):
        if environ['PATH_INFO'].startswith("/json/"):
            # We request a JSON page, no need for auth
            return True
        return options.username == username and options.password == password

    if app.config['DEBUG']:
        # Setting up the cron/ directory with some testing data
        # In production, this is managed by Apache and the json file is going to be override
        # by the cron (see bug 1155935)
        from werkzeug import SharedDataMiddleware
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/cron/': path.join(path.dirname(__file__), 'cron/')
        })

    # We serve (at least) a stastic json file
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/json/': path.join(path.dirname(__file__), 'json/')
    })

    app.wsgi_app = AuthBasicHandler(app.wsgi_app, "Release kick-off", auth)
    app.run(port=options.port, host=options.host)
