# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError


class SanadConsultation(models.Model):
    """A single doctor consultation (PRD 5.2 / 10.3).

    Fields match the PRD exactly: patient, doctor, date, reason,
    symptoms, observations (clinical notes), report, attachments.

    Access is enforced in two layers, deliberately redundant:
    1. ir.rule record rules (security/sanad_medical_record_rules.xml)
       restrict which rows a doctor can even query.
    2. The _check_active_care_relationship constraint below additionally
       blocks CREATE at the ORM level, so a doctor cannot create a
       consultation for a patient they have no active relationship with
       even via direct API/RPC calls that might otherwise slip past a
       record rule race condition (e.g. relationship ended mid-session).
    """
    _name = 'sanad.consultation'
    _description = 'SANAD Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _rec_name = 'display_name'

    medical_record_id = fields.Many2one(
        'sanad.medical.record', string='Medical Record', ondelete='cascade', index=True)
    patient_id = fields.Many2one(
        'sanad.patient', string='Patient', required=True, ondelete='restrict',
        index=True, tracking=True)
    doctor_id = fields.Many2one(
        'sanad.doctor', string='Doctor', required=True, ondelete='restrict',
        index=True, tracking=True, default=lambda self: self._default_doctor())

    date = fields.Datetime(
        string='Date', required=True, default=fields.Datetime.now, tracking=True)
    reason = fields.Char(string='Reason for Visit', required=True)
    symptoms = fields.Text(string='Symptoms')
    observations = fields.Text(string='Medical Observations / Clinical Notes')
    report = fields.Html(string='Report')

    attachment_ids = fields.Many2many(
        'ir.attachment', string='Attachments',
        help='Uploaded documents related to this consultation (referral '
             'letters, external reports, images, etc.)')

    prescription_ids = fields.One2many(
        'sanad.prescription', 'consultation_id', string='Prescriptions')
    prescription_count = fields.Integer(compute='_compute_prescription_count')

    display_name = fields.Char(compute='_compute_display_name')

    @api.model
    def _default_doctor(self):
        doctor = self.env['sanad.doctor'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        return doctor.id if doctor else False

    @api.depends('patient_id', 'doctor_id', 'date')
    def _compute_display_name(self):
        for c in self:
            c.display_name = '%s - %s (%s)' % (
                c.patient_id.display_name or '?',
                c.doctor_id.display_name or '?',
                c.date.strftime('%Y-%m-%d') if c.date else '',
            )

    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for c in self:
            c.prescription_count = len(c.prescription_ids)

    @api.constrains('patient_id', 'doctor_id')
    def _check_active_care_relationship(self):
        rel_model = self.env['sanad.patient.doctor.rel']
        for consultation in self:
            if not consultation.patient_id or not consultation.doctor_id:
                continue
            if self.env.user.has_group('sanad_core.group_sanad_admin'):
                continue
            if not rel_model.has_active_relationship(
                    consultation.patient_id.id, consultation.doctor_id.id):
                raise ValidationError(
                    'This doctor does not have an active care relationship '
                    'with this patient. A care relationship must exist '
                    '(see Care Relationships) before a consultation can be '
                    'recorded.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_id') and not vals.get('medical_record_id'):
                record = self.env['sanad.medical.record'].get_or_create_for_patient(
                    vals['patient_id'])
                vals['medical_record_id'] = record.id
        return super().create(vals_list)
