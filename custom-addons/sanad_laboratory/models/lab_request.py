# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadLabRequest(models.Model):
    """Laboratory analysis request (PRD 5.2 workflow / 10.4).

    Status values match the PRD exactly:
    Draft -> Sent -> Accepted -> Processing -> Completed / Cancelled.

    Workflow (PRD 5.2):
        Doctor -> Analysis Request -> Laboratory -> Result -> Patient Record
    """
    _name = 'sanad.lab.request'
    _description = 'SANAD Laboratory Analysis Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _rec_name = 'display_name'

    patient_id = fields.Many2one(
        'sanad.patient', string='Patient', required=True, ondelete='restrict',
        index=True, tracking=True)
    doctor_id = fields.Many2one(
        'sanad.doctor', string='Doctor', required=True, ondelete='restrict',
        index=True, tracking=True, default=lambda self: self._default_doctor())
    laboratory_id = fields.Many2one(
        'sanad.laboratory.org', string='Laboratory', required=True,
        ondelete='restrict', index=True, tracking=True)
    consultation_id = fields.Many2one(
        'sanad.consultation', string='Related Consultation', ondelete='set null')

    analysis_type = fields.Char(string='Analysis Type', required=True, tracking=True,
                                 help='e.g. "Complete Blood Count", "Fasting Glucose"')
    date = fields.Datetime(string='Request Date', default=fields.Datetime.now, required=True)
    instructions = fields.Text(string='Instructions')

    status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    result_ids = fields.One2many('sanad.lab.result', 'request_id', string='Results')
    result_count = fields.Integer(compute='_compute_result_count')
    display_name = fields.Char(compute='_compute_display_name')

    @api.model
    def _default_doctor(self):
        doctor = self.env['sanad.doctor'].search([('user_id', '=', self.env.uid)], limit=1)
        return doctor.id if doctor else False

    @api.depends('patient_id', 'analysis_type', 'date')
    def _compute_display_name(self):
        for r in self:
            r.display_name = '%s - %s (%s)' % (
                r.patient_id.display_name or '?', r.analysis_type or '',
                r.date.strftime('%Y-%m-%d') if r.date else '')

    @api.depends('result_ids')
    def _compute_result_count(self):
        for r in self:
            r.result_count = len(r.result_ids)

    @api.constrains('patient_id', 'doctor_id')
    def _check_active_care_relationship(self):
        rel_model = self.env['sanad.patient.doctor.rel']
        for request in self:
            if not request.patient_id or not request.doctor_id:
                continue
            if self.env.user.has_group('sanad_core.group_sanad_admin'):
                continue
            if not rel_model.has_active_relationship(request.patient_id.id, request.doctor_id.id):
                raise ValidationError(
                    'This doctor does not have an active care relationship '
                    'with this patient. A laboratory request cannot be '
                    'created without an active care relationship.')

    # ---- Status workflow ----
    def action_send(self):
        for r in self:
            if r.status != 'draft':
                raise ValidationError('Only draft requests can be sent.')
            r.status = 'sent'

    def action_accept(self):
        for r in self:
            if r.status != 'sent':
                raise ValidationError('Only sent requests can be accepted.')
            r.status = 'accepted'

    def action_start_processing(self):
        for r in self:
            if r.status != 'accepted':
                raise ValidationError('Only accepted requests can move to processing.')
            r.status = 'processing'

    def action_complete(self):
        for r in self:
            if r.status != 'processing':
                raise ValidationError('Only requests in processing can be completed.')
            if not r.result_ids:
                raise ValidationError('At least one result must be uploaded before completing.')
            r.status = 'completed'

    def action_cancel(self):
        for r in self:
            if r.status == 'completed':
                raise ValidationError('A completed request cannot be cancelled.')
            r.status = 'cancelled'
