from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

from kickoff.model import Release
from kickoff.views.requests import RequestsAPI, Requests, ReleaseAPI
from kickoff.views.submit import SubmitRelease

app.add_url_rule('/submit_release.html', view_func=SubmitRelease.as_view('submit_release'), methods=['GET', 'POST'])
app.add_url_rule('/requests', view_func=RequestsAPI.as_view('requests_api'), methods=['GET'])
app.add_url_rule('/requests.html', view_func=Requests.as_view('requests'), methods=['GET'])
app.add_url_rule('/requests/<releaseName>', view_func=ReleaseAPI.as_view('release_api'), methods=['POST'])
