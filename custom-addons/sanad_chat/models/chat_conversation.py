# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadChatConversation(models.Model):
    """A secure conversation between two SANAD users (PRD 10.6 / 16).

    Only the pairings the PRD explicitly allows are permitted:
    Doctor<->Patient, Doctor<->Laboratory, Doctor<->Pharmacy.
    This is enforced in _check_allowed_pairing below - not just hidden
    in the UI - so it can't be bypassed via direct RPC calls either.

    Built on mail.thread so messages, attachments, and read/seen state
    reuse Odoo's mature mail subsystem rather than a bespoke
    reimplementation. Real-time delivery to participants uses Odoo's
    native bus.bus (via mail.thread's built-in bus notifications), per
    the approved architecture decision - no separate messaging stack.
    """
    _name = 'sanad.chat.conversation'
    _description = 'SANAD Secure Conversation'
    _inherit = ['mail.thread']
    _order = 'write_date desc'
    _rec_name = 'display_name'

    participant_ids = fields.Many2many(
        'res.users', string='Participants', required=True,
        help='Exactly two participants: a doctor and one of '
             'patient/laboratory-staff/pharmacy-staff.')
    conversation_type = fields.Selection([
        ('doctor_patient', 'Doctor - Patient'),
        ('doctor_laboratory', 'Doctor - Laboratory'),
        ('doctor_pharmacy', 'Doctor - Pharmacy'),
    ], string='Conversation Type', required=True, index=True)

    patient_id = fields.Many2one(
        'sanad.patient', string='Related Patient',
        help='Set for doctor_patient conversations; used to additionally '
             'require an active care relationship between the two parties.')

    display_name = fields.Char(compute='_compute_display_name')
    last_message_date = fields.Datetime(compute='_compute_last_message_date')

    @api.depends('participant_ids')
    def _compute_display_name(self):
        for conv in self:
            names = conv.participant_ids.mapped('name')
            conv.display_name = ' <-> '.join(names) if names else 'New Conversation'

    def _compute_last_message_date(self):
        for conv in self:
            last = conv.message_ids[:1]
            conv.last_message_date = last.date if last else False

    @api.constrains('participant_ids')
    def _check_participants(self):
        for conv in self:
            if len(conv.participant_ids) != 2:
                raise ValidationError(
                    'A conversation must have exactly 2 participants.')

    @api.constrains('participant_ids', 'conversation_type', 'patient_id')
    def _check_allowed_pairing(self):
        """Server-side enforcement of the PRD's allowed conversation
        pairings and, for doctor-patient chats, an active care
        relationship - mirroring the same defense-in-depth pattern used
        for consultations/prescriptions/lab requests in sanad_medical
        and sanad_laboratory."""
        for conv in self:
            users = conv.participant_ids
            doctor = self.env['sanad.doctor'].search([('user_id', 'in', users.ids)], limit=1)
            if not doctor:
                raise ValidationError(
                    'Every SANAD conversation must include exactly one doctor.')
            other_user = users - doctor.user_id

            if conv.conversation_type == 'doctor_patient':
                patient = self.env['sanad.patient'].search(
                    [('user_id', 'in', other_user.ids)], limit=1)
                if not patient:
                    raise ValidationError(
                        'A doctor_patient conversation requires the other '
                        'participant to be a registered patient.')
                if not self.env.user.has_group('sanad_core.group_sanad_admin'):
                    rel_model = self.env['sanad.patient.doctor.rel']
                    if not rel_model.has_active_relationship(patient.id, doctor.id):
                        raise ValidationError(
                            'This doctor has no active care relationship with '
                            'this patient - a conversation cannot be started.')
                conv.patient_id = patient.id

            elif conv.conversation_type == 'doctor_laboratory':
                lab_org = self.env['sanad.laboratory.org'].search(
                    [('user_ids', 'in', other_user.ids)], limit=1)
                if not lab_org:
                    raise ValidationError(
                        'A doctor_laboratory conversation requires the other '
                        'participant to be laboratory staff.')

            elif conv.conversation_type == 'doctor_pharmacy':
                pharmacy_org = self.env['sanad.pharmacy.org'].search(
                    [('user_ids', 'in', other_user.ids)], limit=1)
                if not pharmacy_org:
                    raise ValidationError(
                        'A doctor_pharmacy conversation requires the other '
                        'participant to be pharmacy staff.')

    def action_post_message(self, body):
        """Post a message and notify participants in real time via
        bus.bus. mail.thread.message_post already triggers a bus
        notification to followers/partners automatically in Odoo 19 -
        this wrapper exists so sanad_chat callers (controllers, the
        future React frontend's API layer) have one clear entry point
        rather than needing to know mail internals."""
        self.ensure_one()
        return self.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=self.env.user.partner_id.id,
        )

    @api.model
    def get_or_create_conversation(self, user_id_a, user_id_b, conversation_type, patient_id=False):
        """Idempotent accessor: returns an existing conversation between
        the two users of the given type, or creates one. Used by the
        frontend API layer so 'start chat with my doctor' never creates
        duplicate threads."""
        existing = self.search([
            ('conversation_type', '=', conversation_type),
            ('participant_ids', 'in', [user_id_a]),
            ('participant_ids', 'in', [user_id_b]),
        ], limit=1)
        if existing:
            return existing
        vals = {
            'participant_ids': [(6, 0, [user_id_a, user_id_b])],
            'conversation_type': conversation_type,
        }
        if patient_id:
            vals['patient_id'] = patient_id
        return self.create(vals)
