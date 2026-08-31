# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response

ALLOWED_ACTIONS = {
    'receive': 'action_pharmacy_receive',
    'prepare': 'action_pharmacy_prepare',
    'complete': 'action_pharmacy_complete',
}


def serialize_pharmacy_prescription(p):
    """Deliberately restricted serializer: only the fields PRD 14.3
    grants a pharmacy (medication/dosage/instructions/status), never
    symptoms/observations/report which live on a different model the
    pharmacy group has no access to anyway - this mirrors that same
    restriction at the API layer, not just the Odoo view layer."""
    return {
        'id': p.id,
        'patient_id': p.patient_id.id,
        'patient_name': p.patient_id.name,
        'date': p.date.isoformat() if p.date else None,
        'medication': p.medication,
        'dosage': p.dosage,
        'frequency': p.frequency,
        'duration': p.duration,
        'instructions': p.instructions,
        'pharmacy_status': p.pharmacy_status,
    }


def serialize_pharmacy_org(org):
    return {
        'id': org.id,
        'name': org.name,
        'address': org.address,
        'phone': org.phone,
        'email': org.email,
    }


class SanadPharmacyController(http.Controller):
    """REST endpoints for the pharmacy prescription-processing workflow.
    Row visibility is enforced entirely by the existing record rule
    (rule_sanad_prescription_pharmacy in sanad_medical, scoped to
    pharmacy_id.user_ids) - this controller does not add its own
    filtering logic, it relies on the ORM record rule as the single
    source of truth for access."""

    @http.route('/api/pharmacies', type='http', auth='user', methods=['GET'], csrf=False)
    def list_pharmacies(self, **kwargs):
        """List all active pharmacy organizations.
        Doctors need this to assign a pharmacy when creating a prescription."""
        orgs = request.env['sanad.pharmacy.org'].search(
            [('active', '=', True)], order='name')
        return json_response({
            'pharmacies': [serialize_pharmacy_org(o) for o in orgs]
        })

    @http.route('/api/pharmacy/prescriptions', type='http', auth='user', methods=['GET'], csrf=False)
    def list_pharmacy_prescriptions(self, **kwargs):
        domain = []
        if kwargs.get('status'):
            domain.append(('pharmacy_status', '=', kwargs['status']))
        prescriptions = request.env['sanad.prescription'].search(domain, order='date desc')
        return json_response({
            'prescriptions': [serialize_pharmacy_prescription(p) for p in prescriptions]
        })

    @http.route('/api/pharmacy/prescriptions/<int:prescription_id>/action',
                type='http', auth='user', methods=['POST'], csrf=False)
    def transition_prescription(self, prescription_id, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        action = params.get('action')
        method_name = ALLOWED_ACTIONS.get(action)
        if not method_name:
            return error_response(
                'Invalid action. Allowed: %s' % ', '.join(ALLOWED_ACTIONS.keys()),
                400, 'invalid_action')
        try:
            p = request.env['sanad.prescription'].search(
                [('id', '=', prescription_id)], limit=1)
            if not p:
                return error_response('Prescription not found.', 404, 'not_found')
            getattr(p, method_name)()
            return json_response({'prescription': serialize_pharmacy_prescription(p)})
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')
