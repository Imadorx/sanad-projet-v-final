# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadAiLog(models.Model):
    """Audit log for every AI interaction on the SANAD platform.

    This model exists to satisfy the PRD's hard AI safety requirement
    (Section 15.3 / 19 - AI Testing): it must be possible to prove, after
    the fact, what data an AI request touched, whether PHI was
    anonymized before leaving the platform, and what the outcome was.

    Design notes:
    - Records are created exclusively by server-side code (sanad_ai,
      Phase 8) using sudo(). No security group is granted create/write
      access through the UI/API - this keeps the audit trail
      tamper-resistant from the application layer. Regular users only
      ever get read access, and only to their own records (enforced by
      record rule in security/sanad_record_rules.xml).
    - request_text and response are stored for audit purposes but must
      never themselves contain raw, unredacted patient identifiers -
      it is the responsibility of the sanad_ai anonymization layer
      (Phase 8) to guarantee that before writing here.
    - accessed_model / accessed_record_ids record WHAT authorized data
      was consulted, not its content, so an auditor can verify the AI
      only touched data the requesting user was authorized to see.
    """
    _name = 'sanad.ai.log'
    _description = 'SANAD AI Interaction Audit Log'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    user_id = fields.Many2one(
        'res.users', string='Requesting User', required=True,
        ondelete='restrict', index=True)
    request_type = fields.Selection([
        ('search', 'Intelligent Search'),
        ('explain', 'Document Explanation'),
        ('translate', 'Translation'),
        ('tts', 'Text To Speech'),
    ], string='Request Type', required=True, index=True)
    request_text = fields.Text(
        string='Request',
        help='The user-facing request/question. Must be free of raw PHI '
             'by the time it is logged.')

    accessed_model = fields.Char(
        string='Accessed Model',
        help='Technical name of the Odoo model the AI query was scoped to, '
             'e.g. sanad.lab.result.')
    accessed_record_ids = fields.Char(
        string='Accessed Record IDs',
        help='Comma-separated IDs of the specific records the AI was '
             'authorized to read for this request.')

    anonymization_applied = fields.Boolean(
        string='PHI Anonymized', default=False,
        help='True if patient identifiers were stripped/masked before '
             'any data left the platform for external AI processing.')
    response_metadata = fields.Text(
        string='Response Metadata',
        help='Non-PHI metadata about the AI response: model/provider used, '
             'token counts, latency, safety-filter outcomes. Never the raw '
             'response content if it could contain PHI.')

    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('blocked', 'Blocked'),
    ], string='Status', required=True, default='success', index=True,
        help='blocked = request was refused by the AI safety layer '
             '(e.g. attempted diagnosis or treatment recommendation).')

    timestamp = fields.Datetime(
        string='Timestamp', default=fields.Datetime.now, required=True, index=True)

    display_name = fields.Char(compute='_compute_display_name', store=False)

    def _compute_display_name(self):
        for log in self:
            log.display_name = '%s - %s [%s]' % (
                log.user_id.name or '?',
                dict(self._fields['request_type'].selection).get(log.request_type, ''),
                dict(self._fields['status'].selection).get(log.status, ''),
            )
