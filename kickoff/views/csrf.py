from flask import Response
from flask.views import MethodView
from flask.ext.wtf import Form

def get_csrf_headers():
    form = Form()
    return {'X-CSRF-Token': form.csrf_token._value()}

class CSRFView(MethodView):
    """A simple view that allows an API client to get a CSRF token easily."""
    def get(self):
        return Response(headers=get_csrf_headers())
