import logging
import pytz
import json

from flask import request, jsonify, render_template, Response, redirect, \
    make_response, abort
from flask.views import MethodView

from kickoff import db
from kickoff.log import cef_event, CEF_WARN, CEF_INFO, CEF_ALERT
from kickoff.model import ReleaseEvents
from kickoff.views.forms import ReleaseEventsAPIForm

log = logging.getLogger(__name__)


def sortedEvents():
    def cmpEvents(x, y):
        return cmp(y.sent, x.sent)
    return sorted(ReleaseEvents.getEvents(), cmp=cmpEvents)


class StatusAPI(MethodView):

    def get(self, releaseName):
        status = {'status': {}}
        status['status'] = ReleaseEvents.getStatus(releaseName)
        events = request.args.get('events', type=bool)
        if events:
            status['events'] = []
            rows = ReleaseEvents.query.filter_by(name=releaseName)
            for row in rows:
                status['events'].append(row.toDict())
        return jsonify(status)

    def post(self, releaseName):
        form = ReleaseEventsAPIForm()

        if not form.validate(releaseName):
            errors = form.errors
            log.error('User Input Failed - {} - ({}, {})'.format(errors.values(),                                                                 releaseName,                                                                 form.event_name.data))
            cef_event('User Input Failed', CEF_INFO, **errors)
            return Response(status=400, response=errors.values())

        # Create a ReleaseEvent object from the request data
        try:
            releaseEventsUpdate = ReleaseEvents.createFromForm(releaseName, form)
        except Exception as e:
            log.error('User Input Failed - {} - ({}, {})'.format(e, releaseName,                                                                 form.event_name.data))
            cef_event('User Input Failed', CEF_ALERT)
            return Response(status=400, response=e)

        # Check if this ReleaseEvent already exists in the ReleaseEvents table
        if db.session.query(ReleaseEvents).\
                      filter(ReleaseEvents.name==releaseEventsUpdate.name,
                             ReleaseEvents.event_name==releaseEventsUpdate.event_name).first():
            msg = 'ReleaseEvents ({}, {}) already exists'.\
                   format(releaseEventsUpdate.name, releaseEventsUpdate.event_name)
            log.error('{}'.format(msg))
            cef_event('User Input Failed', CEF_INFO,
                      ReleaseName=releaseEventsUpdate.name)
            return Response(status=400, response=msg)

        # Add a new ReleaseEvents row to the ReleaseEvents table with new data
        db.session.add(releaseEventsUpdate)
        db.session.commit()
        log.debug('({}, {}) - added to the ReleaseEvents table in the database'.
                  format(releaseEventsUpdate.name, releaseEventsUpdate.event_name))

        return Response(status=200)
