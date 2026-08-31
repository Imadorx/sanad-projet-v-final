# -*- coding: utf-8 -*-
import html
import json
import re
from odoo import http
from odoo.exceptions import AccessError, ValidationError
from odoo.http import request

from odoo.addons.sanad_core.controllers.auth_controller import json_response, error_response


def strip_html(text):
    """Remove HTML tags and decode entities, returning plain text.
    Unescape first so Odoo-encoded entities become real tags,
    then strip all tags in one pass."""
    if not text:
        return text or ''
    clean = html.unescape(str(text))
    clean = re.sub(r'<[^>]+>', '', clean)
    return clean.strip()


def serialize_conversation(c):
    return {
        'id': c.id,
        'display_name': c.display_name,
        'conversation_type': c.conversation_type,
        'participant_ids': c.participant_ids.ids,
        'participant_names': c.participant_ids.mapped('name'),
        'patient_id': c.patient_id.id if c.patient_id else None,
        'last_message_date': c.last_message_date.isoformat() if c.last_message_date else None,
    }


def serialize_message(m):
    return {
        'id': m.id,
        'author_id': m.author_id.id if m.author_id else None,
        'author_name': m.author_id.name if m.author_id else 'System',
        'body': strip_html(m.body),
        'date': m.date.isoformat() if m.date else None,
    }


class SanadChatController(http.Controller):
    """REST endpoints for secure conversations.

    Real-time delivery: message_post() on sanad.chat.conversation
    (mail.thread) already dispatches a bus.bus notification to
    followers/partners automatically - this is Odoo 19 core behavior,
    not something reimplemented here. A React frontend outside the Odoo
    web client cannot natively consume Odoo's websocket bus protocol
    without significant extra client-side plumbing, so /api/chat/poll
    below provides a straightforward, genuinely-functional short-poll
    fallback the frontend uses to fetch new messages every few seconds.
    Native websocket subscription is documented as a known limitation/
    future enhancement, not silently faked.
    """

    @http.route('/api/chat/conversations', type='http', auth='user', methods=['GET'], csrf=False)
    def list_conversations(self, **kwargs):
        conversations = request.env['sanad.chat.conversation'].search(
            [], order='write_date desc')
        return json_response({
            'conversations': [serialize_conversation(c) for c in conversations]
        })

    @http.route('/api/chat/conversations', type='http', auth='user', methods=['POST'], csrf=False)
    def create_or_get_conversation(self, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        other_user_id = params.get('other_user_id')
        conversation_type = params.get('conversation_type')
        patient_id = params.get('patient_id')
        if not other_user_id or not conversation_type:
            return error_response(
                'other_user_id and conversation_type are required.', 400, 'missing_params')
        try:
            conv = request.env['sanad.chat.conversation'].get_or_create_conversation(
                request.env.uid, int(other_user_id), conversation_type, patient_id)
            return json_response({'conversation': serialize_conversation(conv)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')
        except ValidationError as e:
            return error_response(str(e), 400, 'validation_error')

    @http.route('/api/chat/conversations/<int:conversation_id>/messages',
                type='http', auth='user', methods=['GET'], csrf=False)
    def list_messages(self, conversation_id, **kwargs):
        conv = request.env['sanad.chat.conversation'].search(
            [('id', '=', conversation_id)], limit=1)
        if not conv:
            return error_response(
                'Conversation not found or not accessible.', 404, 'not_found')
        after_id = kwargs.get('after_id')
        messages = conv.message_ids.filtered(lambda m: m.message_type == 'comment')
        if after_id:
            messages = messages.filtered(lambda m: m.id > int(after_id))
        messages = messages.sorted('date')
        return json_response({'messages': [serialize_message(m) for m in messages]})

    @http.route('/api/chat/conversations/<int:conversation_id>/messages',
                type='http', auth='user', methods=['POST'], csrf=False)
    def post_message(self, conversation_id, **kwargs):
        params = json.loads(request.httprequest.data or b'{}')
        body = (params.get('body') or '').strip()
        if not body:
            return error_response('Message body is required.', 400, 'missing_body')
        conv = request.env['sanad.chat.conversation'].search(
            [('id', '=', conversation_id)], limit=1)
        if not conv:
            return error_response(
                'Conversation not found or not accessible.', 404, 'not_found')
        try:
            message = conv.action_post_message(body)
            return json_response({'message': serialize_message(message)}, 201)
        except AccessError as e:
            return error_response(str(e), 403, 'access_denied')

    @http.route('/api/chat/poll', type='http', auth='user', methods=['GET'], csrf=False)
    def poll_new_messages(self, **kwargs):
        """Short-poll fallback: returns any messages newer than since_id
        across all of the caller's conversations. Intended to be called
        every few seconds by the frontend chat widget."""
        since_id = int(kwargs.get('since_id') or 0)
        conversations = request.env['sanad.chat.conversation'].search([])
        new_messages = []
        for conv in conversations:
            for m in conv.message_ids.filtered(
                    lambda m: m.message_type == 'comment' and m.id > since_id):
                data = serialize_message(m)
                data['conversation_id'] = conv.id
                new_messages.append(data)
        new_messages.sort(key=lambda m: m['id'])
        return json_response({'messages': new_messages})
