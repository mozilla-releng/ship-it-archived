import logging

from flask import Flask, render_template, Response, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

from kickoff.log import cef_event, CEF_WARN
from kickoff.views.csrf import CSRFView
from kickoff.views.releases import ReleasesAPI, Releases, ReleaseAPI, ReleaseL10nAPI, Release
from kickoff.views.submit import SubmitRelease
from kickoff.views.status import StatusAPI

log = logging.getLogger(__name__)

version = '1.1'

# Ensure X-Frame-Options is set to protect against clickjacking attacks:
# https://wiki.mozilla.org/WebAppSec/Secure_Coding_QA_Checklist#Test:_X-Frame-Options
@app.after_request
def add_xframe_options(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

# Apache should always be configured to ask for a login, so we should never
# hit a case where REMOTE_USER isn't set. But just in case...
@app.before_request
def require_login():
    if not request.environ.get('REMOTE_USER'):
        cef_event('Login Required', CEF_WARN)
        return Response(status=401)

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    return render_template('base.html')

@app.route('/favicon.ico')
# The deployed app's web server expects the favicon here.
@app.route('/static/images/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

app.add_url_rule('/submit_release.html', view_func=SubmitRelease.as_view('submit_release'), methods=['GET', 'POST'])
app.add_url_rule('/release.html', view_func=Release.as_view('release'), methods=['GET', 'POST'])
app.add_url_rule('/releases.html', view_func=Releases.as_view('releases'), methods=['GET', 'POST'])
app.add_url_rule('/csrf_token', view_func=CSRFView.as_view('csrf_token'), methods=['GET'])
app.add_url_rule('/releases', view_func=ReleasesAPI.as_view('releases_api'), methods=['GET'])
app.add_url_rule('/releases/<releaseName>', view_func=ReleaseAPI.as_view('release_api'), methods=['GET', 'POST'])
app.add_url_rule('/releases/<releaseName>/l10n', view_func=ReleaseL10nAPI.as_view('release_l10n_api'), methods=['GET'])
app.add_url_rule('/releases/<releaseName>/status', view_func=StatusAPI.as_view('status_api'), methods=['GET', 'POST'])
