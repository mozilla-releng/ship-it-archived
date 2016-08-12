from os import path

from flask import Response, jsonify
# Can't concatenate the next line with the following one. exc is not defined
from flask.ext import sqlalchemy
from sqlalchemy.exc import OperationalError
from kickoff import db


# Wrapper that creates the endpoints required by CloudOps' Dockerflow spec: https://github.com/mozilla-services/Dockerflow
# This gets used by both the admin and public apps.
def create_dockerflow_endpoints(app):
    HEADERS = {"Cache-Control": "no-cache"}

    @app.route("/__version__")
    def version():
        version_file = app.config.get("VERSION_FILE")
        if version_file and path.exists(version_file):
            with open(version_file) as f:
                version_json = f.read()
            return Response(version_json, mimetype="application/json", headers={"Cache-Control": "no-cache"})
        else:
            return jsonify({
                "source": "https://github.com/mozilla/balrog",
                "version": "unknown",
                "commit": "unknown",
            })

    @app.route("/__heartbeat__")
    def heartbeat():
        """Per the Dockerflow spec:
        Respond to /__heartbeat__ with a HTTP 200 or 5xx on error. This should
        depend on services like the database to also ensure they are healthy."""
        try:
            db.engine.execute('SELECT 1').fetchall()
            return Response("OK!", headers=HEADERS)
        except OperationalError:
            return Response("Not OK", status=500, headers=HEADERS)

    @app.route("/__lbheartbeat__")
    def lbheartbeat():
        """Per the Dockerflow spec:
        Respond to /__lbheartbeat__ with an HTTP 200. This is for load balancer
        checks and should not check any dependent services."""
        return Response("OK!", headers=HEADERS)
