# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadPrescription(models.Model):
    """A medication prescription (PRD 5.2 / 10.3).

    Fields match the PRD exactly: medication, dosage, frequency,
    duration, instructions - plus patient/doctor/date linkage and a
    status workflow so sanad_pharmacy (Phase 5) has a well-defined
    state machine to consume.
    """
    _name = 'sanad.prescription'
    _description = 'SANAD Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _rec_name = 'display_name'

    medical_record_id = fields.Many2one(
        'sanad.medical.record', string='Medical Record', ondelete='cascade', index=True)
    consultation_id = fields.Many2one(
        'sanad.consultation', string='Related Consultation', ondelete='set null')
    patient_id = fields.Many2one(
        'sanad.patient', string='Patient', required=True, ondelete='restrict',
        index=True, tracking=True)
    doctor_id = fields.Many2one(
        'sanad.doctor', string='Doctor', required=True, ondelete='restrict',
        index=True, tracking=True, default=lambda self: self._default_doctor())

    date = fields.Datetime(
        string='Date', required=True, default=fields.Datetime.now, tracking=True)

    medication = fields.Char(string='Medication', required=True, tracking=True)
    dosage = fields.Char(string='Dosage', required=True,
                          help='e.g. "500mg"')
    frequency = fields.Char(string='Frequency', required=True,
                             help='e.g. "3 times per day"')
    duration = fields.Char(string='Duration', required=True,
                            help='e.g. "7 days"')
    instructions = fields.Text(string='Instructions')

    # Pharmacy workflow status - defined here so sanad_pharmacy (Phase 5)
    # can update it without needing write access to clinical fields.
    pharmacy_status = fields.Selection([
        ('pending', 'Pending'),
        ('received', 'Received by Pharmacy'),
        ('prepared', 'Prepared'),
        ('completed', 'Completed'),
    ], string='Pharmacy Status', default='pending', tracking=True)
    pharmacy_id = fields.Many2one(
        'sanad.pharmacy.org', string='Assigned Pharmacy', tracking=True)

    display_name = fields.Char(compute='_compute_display_name')

    @api.model
    def _default_doctor(self):
        doctor = self.env['sanad.doctor'].search(
            [('user_id', '=', self.env.uid)], limit=1)
        return doctor.id if doctor else False

    @api.depends('patient_id', 'medication', 'date')
    def _compute_display_name(self):
        for p in self:
            p.display_name = '%s - %s (%s)' % (
                p.patient_id.display_name or '?',
                p.medication or '',
                p.date.strftime('%Y-%m-%d') if p.date else '',
            )

    @api.constrains('patient_id', 'doctor_id')
    def _check_active_care_relationship(self):
        rel_model = self.env['sanad.patient.doctor.rel']
        for prescription in self:
            if not prescription.patient_id or not prescription.doctor_id:
                continue
            if self.env.user.has_group('sanad_core.group_sanad_admin'):
                continue
            if not rel_model.has_active_relationship(
                    prescription.patient_id.id, prescription.doctor_id.id):
                raise ValidationError(
                    'This doctor does not have an active care relationship '
                    'with this patient. A prescription cannot be created '
                    'without an active care relationship.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_id') and not vals.get('medical_record_id'):
                record = self.env['sanad.medical.record'].get_or_create_for_patient(
                    vals['patient_id'])
                vals['medical_record_id'] = record.id
        return super().create(vals_list)
