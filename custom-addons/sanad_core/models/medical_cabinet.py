# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadMedicalCabinet(models.Model):
    """A medical cabinet (doctor's office / clinic) organization.

    This is an organizational entity, not a patient-facing model.
    It intentionally holds only the minimal contact fields needed for
    dropdowns and administration; it does not duplicate res.partner's
    full addressing capabilities. If richer address/contact management
    is needed later, this model should link to a res.partner record
    instead of growing its own fields.
    """
    _name = 'sanad.medical.cabinet'
    _description = 'SANAD Medical Cabinet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Cabinet Name', required=True, tracking=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    active = fields.Boolean(default=True)

    doctor_ids = fields.One2many(
        'sanad.doctor', 'cabinet_id', string='Doctors')
    doctor_count = fields.Integer(
        string='Doctor Count', compute='_compute_doctor_count')

    def _compute_doctor_count(self):
        for cabinet in self:
            cabinet.doctor_count = len(cabinet.doctor_ids)
