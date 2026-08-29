# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response


def serialize_consultation(c):
    return {
        'id': c.id,
        'patient_id': c.patient_id.id,
        'patient_name': c.patient_id.name,
        'doctor_id': c.doctor_id.id,
        'doctor_name': c.doctor_id.name,
        'date': c.date.isoformat() if c.date else None,
        'reason': c.reason,
        'symptoms': c.symptoms,
        'observations': c.observations,
        'report': c.report,
        'prescription_count': c.prescription_count,
    }


def serialize_prescription(p):
    return {
        'id': p.id,
        'patient_id': p.patient_id.id,
        'patient_name': p.patient_id.name,
        'doctor_id': p.doctor_id.id,
        'doctor_name': p.doctor_id.name,
        'consultation_id': p.consultation_id.id if p.consultation_id else None,
        'date': p.date.isoformat() if p.date else None,
        'medication': p.medication,
        'dosage': p.dosage,
        'frequency': p.frequency,
        'duration': p.duration,
        'instructions': p.instructions,
        'pharmacy_status': p.pharmacy_status,
        'pharmacy_id': p.pharmacy_id.id if p.pharmacy_id else None,
    }


def serialize_medical_record(m):
    return {
        'id': m.id,
        'patient_id': m.patient_id.id,
        'consultation_count': m.consultation_count,
        'prescription_count': m.prescription_count,
        'last_consultation_date': m.last_consultation_date.isoformat() if m.last_consultation_date else None,
        'consultations': [serialize_consultation(c) for c in m.consultation_ids],
        'prescriptions': [serialize_prescription(p) for p in m.prescription_ids],
    }


class SanadMedicalController(http.Controller):
    """REST endpoints for medical records, consultations and prescriptions.
    auth='user' throughout - record rules from sanad_medical apply
    automatically (doctor sees only assigned patients, patient sees only
    their own data)."""

    # ---- Medical Record ----
    @http.route('/api/medical-records/<int:patient_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_medical_record(self, patient_id, **kwargs):
        record = request.env['sanad.medical.record'].search([('patient_id', '=', patient_id)], limit=1)
        if not record:
            return error_response('No medical record found for this patient.', 404, 'not_found')
        return json_response({'medical_record': serialize_medical_record(record)})

    # ---- Consultations ----
    @http.route('/api/consultations', type='http', auth='user', methods=['GET'], csrf=False)
    def list_consultations(self, **kwargs):
        domain = []
        if kwargs.get('patient_id'):
            domain.append(('patient_id', '=', int(kwargs['patient_id'])))
        consultations = request.env['sanad.consultation'].search(domain, order='date desc')
        return json_response({'consultations': [serialize_consultation(c) for c in consultations]})

    @http.route('/api/consultations/<int:consultation_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_consultation(self, consultation_id, **kwargs):
        c = request.env['sanad.consultation'].search([('id', '=', consultation_id)], limit=1)
        if not c:
            return error_response('Consultation not found.', 404, 'not_found')
        return json_response({'consultation': serialize_consultation(c)})

    @http.route('/api/consultations', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def create_consultation(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            c = request.env['sanad.consultation'].create(params)
            return json_response({'consultation': serialize_consultation(c)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    # ---- Prescriptions ----
    @http.route('/api/prescriptions', type='http', auth='user', methods=['GET'], csrf=False)
    def list_prescriptions(self, **kwargs):
        domain = []
        if kwargs.get('patient_id'):
            domain.append(('patient_id', '=', int(kwargs['patient_id'])))
        prescriptions = request.env['sanad.prescription'].search(domain, order='date desc')
        return json_response({'prescriptions': [serialize_prescription(p) for p in prescriptions]})

    @http.route('/api/prescriptions', type='jsonrpc', auth='user', methods=['POST'], csrf=False)
    def create_prescription(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        try:
            p = request.env['sanad.prescription'].create(params)
            return json_response({'prescription': serialize_prescription(p)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')
