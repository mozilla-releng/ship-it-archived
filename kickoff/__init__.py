from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

from kickoff.model import Release
from kickoff.views.releases import ReleasesAPI, Releases, ReleaseAPI
from kickoff.views.submit import SubmitRelease

app.add_url_rule('/submit_release.html', view_func=SubmitRelease.as_view('submit_release'), methods=['GET', 'POST'])
app.add_url_rule('/releases', view_func=ReleasesAPI.as_view('releases_api'), methods=['GET'])
app.add_url_rule('/releases.html', view_func=Releases.as_view('releases'), methods=['GET'])
app.add_url_rule('/releases/<releaseName>', view_func=ReleaseAPI.as_view('release_api'), methods=['GET', 'POST'])
