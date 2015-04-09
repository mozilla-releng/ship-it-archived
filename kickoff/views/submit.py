import logging

from flask import request, render_template, redirect, make_response, Response
from flask.views import MethodView

from kickoff import db
from kickoff.log import cef_event, CEF_ALERT, CEF_INFO
from kickoff.model import getReleaseTable
from kickoff.views.forms import FennecReleaseForm, FirefoxReleaseForm, \
    ThunderbirdReleaseForm, getReleaseForm

log = logging.getLogger(__name__)


class SubmitRelease(MethodView):
    def get(self):
        return render_template('submit_release.html', fennecForm=FennecReleaseForm(),
                               firefoxForm=FirefoxReleaseForm(),
                               thunderbirdForm=ThunderbirdReleaseForm())

    def post(self):
        # This is checked for in a before_request hook.
        submitter = request.environ.get('REMOTE_USER')
        # We need copies of all the forms to reprint the page if there's any
        # errors. The form that was actually submitted will get overridden with
        # data later on.
        forms = {
            'fennecForm': FennecReleaseForm(formdata=None),
            'firefoxForm': FirefoxReleaseForm(formdata=None),
            'thunderbirdForm': ThunderbirdReleaseForm(formdata=None)
        }

        for field, value in request.form.items():
            if field.endswith('product'):
                product = value
                break

        try:
            form = getReleaseForm(product)()
        except ValueError:
            cef_event('User Input Failed', CEF_ALERT, ProductName=product)
            return Response(status=400,
                            response="Unknown product name '%s'" % product)
        errors = []
        if not form.validate():
            cef_event('User Input Failed', CEF_INFO, **form.errors)
            for error in form.errors.values():
                errors.extend(error)

        table = getReleaseTable(form.product.data)
        release = table.createFromForm(submitter, form)

        if db.session.query(table).filter(table.name == release.name).first():
            msg = 'Release "%s" already exists' % release.name
            cef_event('User Input Failed', CEF_INFO, ReleaseName=release.name)
            errors.append(msg)
        if errors:
            forms['%sForm' % product] = getReleaseForm(product)()
            return make_response(
                render_template('submit_release.html', errors=errors,
                                selectedProduct=product, **forms), 400
            )

        db.session.add(release)
        db.session.commit()
        log.debug('%s added to the database', release.name)
        return redirect('releases.html')
