# -*- coding: utf-8 -*-
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


def json_response(data, status=200):
    """Uniform JSON response helper used across all SANAD API controllers."""
    return request.make_response(
        json.dumps(data),
        status=status,
        headers=[('Content-Type', 'application/json')],
    )


def error_response(message, status=400, code='error'):
    return json_response({'error': True, 'code': code, 'message': message}, status=status)


def current_user_roles(user):
    """Return the list of SANAD role technical names the user holds -
    used by the frontend to decide which dashboard/menu to render."""
    roles = []
    for xml_id in ['sanad_core.group_sanad_admin', 'sanad_core.group_sanad_doctor',
                    'sanad_core.group_sanad_patient', 'sanad_core.group_sanad_laboratory',
                    'sanad_core.group_sanad_pharmacy']:
        if user.has_group(xml_id):
            roles.append(xml_id.split('.')[-1].replace('group_sanad_', ''))
    return roles


def serialize_user(user):
    doctor = request.env['sanad.doctor'].sudo().search([('user_id', '=', user.id)], limit=1)
    patient = request.env['sanad.patient'].sudo().search([('user_id', '=', user.id)], limit=1)
    return {
        'id': user.id,
        'name': user.name,
        'login': user.login,
        'email': user.email,
        'roles': current_user_roles(user),
        'doctor_id': doctor.id if doctor else None,
        'patient_id': patient.id if patient else None,
    }


class SanadAuthController(http.Controller):
    """Session-based authentication for the SANAD React frontend.

    Uses Odoo's native session/cookie authentication (request.session.authenticate)
    rather than a bespoke token scheme, per PRD 14.2 ("Authentication managed
    through Odoo users system / Secure sessions"). The React app sends
    credentials via axios `withCredentials: true` and the session cookie
    set here is then reused automatically for all subsequent /api/* calls
    below, which use auth='user'.
    """

    @http.route('/api/auth/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        login = params.get('login')
        password = params.get('password')
        db = request.db or params.get('db') or 'sanad_db'
        if not login or not password:
            return error_response('Login and password are required.', 400, 'missing_credentials')
        try:
            auth_info = request.session.authenticate(request.env, {'login': login, 'password': password, 'type': 'password'})
            uid = auth_info.get('uid')
        except Exception:
            _logger.warning('SANAD login failure for %s', login)
            return error_response('Invalid credentials.', 401, 'invalid_credentials')
        if not uid:
            return error_response('Invalid credentials.', 401, 'invalid_credentials')
        user = request.env['res.users'].browse(uid)
        return json_response({'user': serialize_user(user)})

    @http.route('/api/auth/logout', type='http', auth='user', methods=['POST'], csrf=False)
    def logout(self, **kwargs):
        request.session.logout(keep_db=True)
        return json_response({'success': True})

    @http.route('/api/auth/session', type='http', auth='user', methods=['GET', 'POST'], csrf=False)
    def session_info(self, **kwargs):
        return json_response({'user': serialize_user(request.env.user)})
