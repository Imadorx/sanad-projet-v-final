# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadPatientDoctorRel(models.Model):
    """Patient-Doctor care relationship.

    This is the access-control backbone referenced throughout the PRD's
    RBAC section (14.3): a doctor may only access a patient's medical
    record, consultations, prescriptions and lab results if an ACTIVE
    relationship row exists here. sanad_medical, sanad_laboratory and
    sanad_pharmacy record rules all key off this model rather than
    inferring access from consultation history, keeping the access
    check a simple indexed lookup instead of an expensive join.

    Deliberately placed in sanad_patient (not sanad_core) since it
    depends on sanad.patient, which does not exist at the sanad_core
    level - see the Phase 1 approval note.
    """
    _name = 'sanad.patient.doctor.rel'
    _description = 'SANAD Patient-Doctor Care Relationship'
    _inherit = ['mail.thread']
    _order = 'start_date desc'
    _rec_name = 'display_name'

    patient_id = fields.Many2one(
        'sanad.patient', string='Patient', required=True,
        ondelete='cascade', index=True, tracking=True)
    doctor_id = fields.Many2one(
        'sanad.doctor', string='Doctor', required=True,
        ondelete='cascade', index=True, tracking=True)
    cabinet_id = fields.Many2one(
        related='doctor_id.cabinet_id', string='Cabinet', store=True, readonly=True)

    relationship_type = fields.Selection([
        ('primary', 'Primary Care'),
        ('consulting', 'Consulting'),
        ('referred', 'Referred'),
    ], string='Relationship Type', required=True, default='consulting', tracking=True)

    start_date = fields.Date(
        string='Start Date', default=fields.Date.today, required=True, tracking=True)
    end_date = fields.Date(
        string='End Date', tracking=True,
        help='Leave empty for an ongoing relationship. Setting this in the '
             'past automatically deactivates the relationship.')
    active = fields.Boolean(
        string='Active', default=True, tracking=True,
        help='Controls whether this doctor currently has access to the '
             'patient record. Automatically set to False when End Date '
             'is reached (see _cron_deactivate_expired).')

    notes = fields.Text(string='Notes')
    display_name = fields.Char(compute='_compute_display_name')

    # Odoo 19: _sql_constraints removed - use models.Constraint attributes.
    _patient_doctor_uniq = models.Constraint(
        'unique(patient_id, doctor_id, relationship_type)',
        'This exact care relationship already exists for this patient and doctor.',
    )

    @api.depends('patient_id', 'doctor_id', 'relationship_type')
    def _compute_display_name(self):
        for rel in self:
            rel.display_name = '%s - %s (%s)' % (
                rel.patient_id.display_name or '?',
                rel.doctor_id.display_name or '?',
                dict(self._fields['relationship_type'].selection).get(rel.relationship_type, ''),
            )

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rel in self:
            if rel.end_date and rel.start_date and rel.end_date < rel.start_date:
                raise ValidationError('End date cannot be before start date.')

    def write(self, vals):
        res = super().write(vals)
        if 'end_date' in vals:
            today = fields.Date.today()
            for rel in self:
                if rel.end_date and rel.end_date <= today and rel.active:
                    rel.active = False
        return res

    @api.model
    def _cron_deactivate_expired(self):
        """Scheduled action: deactivate relationships whose end_date has
        passed. Access-control-critical, so this runs independently of
        any UI interaction rather than relying on someone opening the
        record."""
        today = fields.Date.today()
        expired = self.search([
            ('active', '=', True),
            ('end_date', '!=', False),
            ('end_date', '<=', today),
        ])
        expired.write({'active': False})

    @api.model
    def has_active_relationship(self, patient_id, doctor_id):
        """Server-side helper used by other modules' record rules /
        controllers to check access without duplicating query logic."""
        return bool(self.search_count([
            ('patient_id', '=', patient_id),
            ('doctor_id', '=', doctor_id),
            ('active', '=', True),
        ]))
