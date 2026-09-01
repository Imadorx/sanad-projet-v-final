# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response

ALLOWED_ACTIONS = {
    'send': 'action_send',
    'accept': 'action_accept',
    'start_processing': 'action_start_processing',
    'complete': 'action_complete',
    'cancel': 'action_cancel',
}


def serialize_lab_request(r):
    return {
        'id': r.id,
        'patient_id': r.patient_id.id,
        'patient_name': r.patient_id.name,
        'doctor_id': r.doctor_id.id,
        'doctor_name': r.doctor_id.name,
        'laboratory_id': r.laboratory_id.id,
        'laboratory_name': r.laboratory_id.name,
        'consultation_id': r.consultation_id.id if r.consultation_id else None,
        'analysis_type': r.analysis_type,
        'date': r.date.isoformat() if r.date else None,
        'instructions': r.instructions,
        'status': r.status,
        'result_count': r.result_count,
    }


def serialize_lab_result(res):
    return {
        'id': res.id,
        'request_id': res.request_id.id,
        'patient_id': res.patient_id.id,
        'analysis_name': res.analysis_name,
        'result_value': res.result_value,
        'unit': res.unit,
        'reference_range': res.reference_range,
        'is_out_of_range': res.is_out_of_range,
        'date': res.date.isoformat() if res.date else None,
        'document_filename': res.document_filename,
    }


def serialize_laboratory_org(org):
    return {
        'id': org.id,
        'name': org.name,
        'address': org.address,
        'phone': org.phone,
        'email': org.email,
    }


class SanadLaboratoryController(http.Controller):
    """REST endpoints for laboratory requests, results, and KPI evolution.
    All business logic (status transitions, validation) stays on the
    sanad.lab.request/sanad.lab.result models - these routes only
    translate HTTP <-> ORM calls and never re-implement workflow rules."""

    @http.route('/api/laboratories', type='http', auth='user', methods=['GET'], csrf=False)
    def list_laboratories(self, **kwargs):
        orgs = request.env['sanad.laboratory.org'].search(
            [('active', '=', True)], order='name')
        return json_response({
            'laboratories': [serialize_laboratory_org(o) for o in orgs]
        })

    # ---- Requests ----
    @http.route('/api/lab-requests', type='http', auth='user', methods=['GET'], csrf=False)
    def list_lab_requests(self, **kwargs):
        domain = []
        if kwargs.get('patient_id'):
            domain.append(('patient_id', '=', int(kwargs['patient_id'])))
        if kwargs.get('status'):
            domain.append(('status', '=', kwargs['status']))
        requests_ = request.env['sanad.lab.request'].search(domain, order='date desc')
        return json_response({'lab_requests': [serialize_lab_request(r) for r in requests_]})

    @http.route('/api/lab-requests/<int:request_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_lab_request(self, request_id, **kwargs):
        r = request.env['sanad.lab.request'].search([('id', '=', request_id)], limit=1)
        if not r:
            return error_response('Laboratory request not found.', 404, 'not_found')
        data = serialize_lab_request(r)
        data['results'] = [serialize_lab_result(res) for res in r.result_ids]
        return json_response({'lab_request': data})

    @http.route('/api/lab-requests', type='http', auth='user', methods=['POST'], csrf=False)
    def create_lab_request(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            r = request.env['sanad.lab.request'].create(params)
            return json_response({'lab_request': serialize_lab_request(r)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    @http.route('/api/lab-requests/<int:request_id>/action', type='http', auth='user', methods=['POST'], csrf=False)
    def transition_lab_request(self, request_id, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        action = params.get('action')
        method_name = ALLOWED_ACTIONS.get(action)
        if not method_name:
            return error_response(
                'Invalid action. Allowed: %s' % ', '.join(ALLOWED_ACTIONS.keys()),
                400, 'invalid_action')
        try:
            r = request.env['sanad.lab.request'].search([('id', '=', request_id)], limit=1)
            if not r:
                return error_response('Laboratory request not found.', 404, 'not_found')
            getattr(r, method_name)()
            return json_response({'lab_request': serialize_lab_request(r)})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    # ---- Results ----
    @http.route('/api/lab-results', type='http', auth='user', methods=['GET'], csrf=False)
    def list_lab_results(self, **kwargs):
        domain = []
        if kwargs.get('patient_id'):
            domain.append(('patient_id', '=', int(kwargs['patient_id'])))
        if kwargs.get('request_id'):
            domain.append(('request_id', '=', int(kwargs['request_id'])))
        results = request.env['sanad.lab.result'].search(domain, order='date desc')
        return json_response({'lab_results': [serialize_lab_result(r) for r in results]})

    @http.route('/api/lab-results', type='http', auth='user', methods=['POST'], csrf=False)
    def create_lab_result(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            r = request.env['sanad.lab.result'].create(params)
            return json_response({'lab_result': serialize_lab_result(r)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    # ---- KPI Evolution ----
    @http.route('/api/lab-results/kpi', type='http', auth='user', methods=['GET'], csrf=False)
    def kpi_evolution(self, **kwargs):
        patient_id = kwargs.get('patient_id')
        analysis_name = kwargs.get('analysis_name')
        if not patient_id or not analysis_name:
            return error_response('patient_id and analysis_name are required.', 400, 'missing_params')
        try:
            # Delegates to the model helper (business logic lives on the
            # model, not duplicated here) - it already applies normal
            # record-rule-scoped search, so an unauthorized caller gets
            # an empty series rather than another patient's data.
            data = request.env['sanad.lab.result'].get_kpi_evolution(
                int(patient_id), analysis_name)
            serialized = [
                {'date': d['date'].isoformat() if d['date'] else None,
                 'value': d['value'], 'unit': d['unit']}
                for d in data
            ]
            return json_response({'analysis_name': analysis_name, 'evolution': serialized})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
