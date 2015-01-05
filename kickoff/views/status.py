import logging

from flask import request, jsonify, render_template, Response
from flask.views import MethodView

from kickoff import db
from kickoff.log import cef_event, CEF_INFO, CEF_ALERT
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
            log.error('User Input Failed - %s - (%s, %s)', errors.values(),
                      releaseName, form.event_name.data)
            cef_event('User Input Failed', CEF_INFO, **errors)
            return Response(status=400, response=errors.values())

        # Create a ReleaseEvent object from the request data
        try:
            releaseEventsUpdate = ReleaseEvents.createFromForm(releaseName,
                                                               form)
        except Exception as e:
            log.error('User Input Failed - %s - (%s, %s)', e, releaseName,
                      form.event_name.data)
            cef_event('User Input Failed', CEF_ALERT)
            return Response(status=400, response=e)

        # Check if this ReleaseEvent already exists in the ReleaseEvents table
        if db.session.query(ReleaseEvents).filter(
            ReleaseEvents.name == releaseEventsUpdate.name,
            ReleaseEvents.event_name == releaseEventsUpdate.event_name
        ).first():
            msg = 'ReleaseEvents ({r_name}, {e_name}) already exists'.format(
                r_name=releaseEventsUpdate.name,
                e_name=releaseEventsUpdate.event_name)
            log.error(msg)
            cef_event('User Input Failed', CEF_INFO,
                      ReleaseName=releaseEventsUpdate.name)
            return Response(status=400, response=msg)

        # Add a new ReleaseEvents row to the ReleaseEvents table with new data
        db.session.add(releaseEventsUpdate)
        db.session.commit()
        log.debug('(%s, %s) - added to the ReleaseEvents',
                  releaseEventsUpdate.name, releaseEventsUpdate.event_name)

        return Response(status=200)


class StatusesAPI(MethodView):

    def get(self):
        group = request.args.get('group')
        if not group:
            cef_event('User Input Failed', CEF_INFO, group=group)
            return Response(status=400,
                            response="Got unparseable value for group")
        events = [(r.name, r.event_name) for r in
                  ReleaseEvents.getEvents(group)]
        return jsonify({'events': events})


class Status(MethodView):

    def get(self, releaseName):
        status_groups = [('tag', 'Tagging'), ('build', 'Builds'),
                         ('repack', 'Repacks'), ('update', 'Update'),
                         ('releasetest', 'Release Test'),
                         ('readyforrelease', 'Ready For Release'),
                         ('postrelease', 'Post Release')]
        status = ReleaseEvents.getStatus(releaseName)
        errors = {}
        if not status:
            errors = ['No release events found for {0}'.format(releaseName)]
        return render_template(
            'status.html', status=ReleaseEvents.getStatus(releaseName),
            status_groups=status_groups, errors=errors)


class Statuses(MethodView):

    def get(self):
        return render_template('statuses.html', statuses=sortedEvents())
