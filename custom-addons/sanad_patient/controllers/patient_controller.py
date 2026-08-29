# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response


def serialize_patient(p):
    return {
        'id': p.id,
        'name': p.name,
        'phone': p.phone,
        'email': p.email,
        'address': p.address,
        'birth_date': p.birth_date.isoformat() if p.birth_date else None,
        'age': p.age,
        'gender': p.gender,
        'blood_group': p.blood_group,
        'allergies': p.allergies,
        'chronic_diseases': p.chronic_diseases,
        'medical_notes': p.medical_notes,
        'emergency_contact_name': p.emergency_contact_name,
        'emergency_contact_phone': p.emergency_contact_phone,
        'emergency_contact_relation': p.emergency_contact_relation,
        'doctor_ids': p.doctor_ids.ids,
        'active': p.active,
    }


def serialize_care_rel(r):
    return {
        'id': r.id,
        'patient_id': r.patient_id.id,
        'patient_name': r.patient_id.name,
        'doctor_id': r.doctor_id.id,
        'doctor_name': r.doctor_id.name,
        'relationship_type': r.relationship_type,
        'start_date': r.start_date.isoformat() if r.start_date else None,
        'end_date': r.end_date.isoformat() if r.end_date else None,
        'active': r.active,
    }


class SanadPatientController(http.Controller):
    """REST endpoints for sanad.patient and sanad.patient.doctor.rel.

    All routes use auth='user': the endpoint runs as the logged-in
    Odoo user, so every ir.rule record rule built in Phase 2 applies
    automatically to the underlying search/read/write/create calls -
    the controller does not re-implement RBAC, it inherits it.
    """

    @http.route('/api/patients', type='http', auth='user', methods=['GET'], csrf=False)
    def list_patients(self, **kwargs):
        try:
            patients = request.env['sanad.patient'].search([])
            return json_response({'patients': [serialize_patient(p) for p in patients]})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')

    @http.route('/api/patients/me', type='http', auth='user', methods=['GET'], csrf=False)
    def my_patient_profile(self, **kwargs):
        patient = request.env['sanad.patient'].search([('user_id', '=', request.env.uid)], limit=1)
        if not patient:
            return error_response('No patient profile linked to this account.', 404, 'not_found')
        return json_response({'patient': serialize_patient(patient)})

    @http.route('/api/patients/<int:patient_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_patient(self, patient_id, **kwargs):
        try:
            # search (not browse) so record rules filter the result set -
            # a patient outside the caller's access simply won't be found,
            # rather than being fetchable and only failing on field read.
            patient = request.env['sanad.patient'].search([('id', '=', patient_id)], limit=1)
            if not patient:
                return error_response('Patient not found.', 404, 'not_found')
            return json_response({'patient': serialize_patient(patient)})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')

    @http.route('/api/patients', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def create_patient(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            patient = request.env['sanad.patient'].create(params)
            return json_response({'patient': serialize_patient(patient)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    @http.route('/api/patients/<int:patient_id>', type='jsonrpc', auth='user', methods=['PUT'], csrf=False)
    def update_patient(self, patient_id, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            patient = request.env['sanad.patient'].browse(patient_id)
            patient.write(params)
            return json_response({'patient': serialize_patient(patient)})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    @http.route('/api/care-relationships', type='http', auth='user', methods=['GET'], csrf=False)
    def list_care_relationships(self, **kwargs):
        patient_id = kwargs.get('patient_id')
        domain = [('patient_id', '=', int(patient_id))] if patient_id else []
        try:
            rels = request.env['sanad.patient.doctor.rel'].search(domain)
            return json_response({'relationships': [serialize_care_rel(r) for r in rels]})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')

    @http.route('/api/care-relationships', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def create_care_relationship(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            rel = request.env['sanad.patient.doctor.rel'].create(params)
            return json_response({'relationship': serialize_care_rel(rel)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')
