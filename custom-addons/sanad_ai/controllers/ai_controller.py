# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response


class SanadAiController(http.Controller):
    """REST endpoints for the SANAD AI assistant. Every route delegates
    immediately to sanad.ai.assistant (models/ai_assistant.py) - the
    controller does not touch anonymization, provider selection, safety
    filtering, or audit logging itself. This keeps the safety pipeline
    defined in exactly one place."""

    @http.route('/api/ai/search', type='http', auth='user', methods=['POST'], csrf=False)
    def ai_search(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        query = (params.get('query') or '').strip()
        patient_id = params.get('patient_id')
        if not query:
            return error_response('query is required.', 400, 'missing_query')
        try:
            result = request.env['sanad.ai.assistant'].authorized_search(
                query, patient_id=int(patient_id) if patient_id else None)
            return json_response(result)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except UserError as e:
            return error_response(str(e), 503, 'ai_unavailable')

    @http.route('/api/ai/explain', type='http', auth='user', methods=['POST'], csrf=False)
    def ai_explain(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        model_name = params.get('model')
        record_id = params.get('record_id')
        if not model_name or not record_id:
            return error_response('model and record_id are required.', 400, 'missing_params')
        try:
            result = request.env['sanad.ai.assistant'].explain_record(model_name, int(record_id))
            return json_response(result)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except UserError as e:
            return error_response(str(e), 503, 'ai_unavailable')

    @http.route('/api/ai/translate', type='http', auth='user', methods=['POST'], csrf=False)
    def ai_translate(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        text = (params.get('text') or '').strip()
        target_lang = params.get('target_lang')
        if not text or not target_lang:
            return error_response('text and target_lang are required.', 400, 'missing_params')
        try:
            result = request.env['sanad.ai.assistant'].translate_text(text, target_lang)
            return json_response(result)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except UserError as e:
            return error_response(str(e), 503, 'ai_unavailable')

    @http.route('/api/ai/tts', type='http', auth='user', methods=['POST'], csrf=False)
    def ai_tts(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        text = (params.get('text') or '').strip()
        if not text:
            return error_response('text is required.', 400, 'missing_text')
        result = request.env['sanad.ai.assistant'].request_tts(text)
        return json_response(result)
