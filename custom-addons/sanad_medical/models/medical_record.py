# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SanadMedicalRecord(models.Model):
    """One summary medical record per patient - the parent container for
    consultations, prescriptions, and (from Phase 4) laboratory results,
    matching the PRD's entity relationship (Section 11):
    Patient -> Medical Record -> Consultations -> Prescriptions -> Lab Results.

    This model itself stores no clinical content directly; it aggregates
    and summarizes what already lives on sanad.consultation and
    sanad.prescription, giving doctors a single entry point into a
    patient's full history (PRD 5.2 "Patient Follow-up").
    """
    _name = 'sanad.medical.record'
    _description = 'SANAD Medical Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'

    patient_id = fields.Many2one(
        'sanad.patient', string='Patient', required=True, ondelete='cascade',
        index=True)
    consultation_ids = fields.One2many(
        'sanad.consultation', 'medical_record_id', string='Consultations')
    prescription_ids = fields.One2many(
        'sanad.prescription', 'medical_record_id', string='Prescriptions')

    consultation_count = fields.Integer(compute='_compute_counts')
    prescription_count = fields.Integer(compute='_compute_counts')
    last_consultation_date = fields.Date(compute='_compute_counts')

    # Odoo 19: _sql_constraints was removed in favor of models.Constraint
    # class attributes (name must start with '_' to avoid clashing with
    # field names). See: odoo.com/documentation/19.0/developer/reference/backend/orm.html
    _patient_uniq = models.Constraint(
        'unique(patient_id)',
        'A medical record already exists for this patient.',
    )

    @api.depends('consultation_ids', 'prescription_ids')
    def _compute_counts(self):
        for rec in self:
            rec.consultation_count = len(rec.consultation_ids)
            rec.prescription_count = len(rec.prescription_ids)
            dates = rec.consultation_ids.mapped('date')
            rec.last_consultation_date = max(dates).date() if dates else False

    @api.model
    def get_or_create_for_patient(self, patient_id):
        """Idempotent accessor used by sanad.consultation.create() so a
        medical record is transparently provisioned on a patient's first
        consultation rather than requiring a separate manual step."""
        record = self.search([('patient_id', '=', patient_id)], limit=1)
        if not record:
            record = self.create({'patient_id': patient_id})
        return record
