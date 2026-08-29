# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadPatient(models.Model):
    """Patient medical profile.

    Identity (full name, DOB, gender, phone, email, address) is sourced
    from res.partner (and res.users where the patient has portal/app
    login access), exactly as for sanad.doctor in sanad_core. This model
    only carries the healthcare-domain fields listed in the PRD
    (Section 5.2 / 10.2): blood group, allergies, chronic diseases,
    emergency contact, medical notes.
    """
    _name = 'sanad.patient'
    _description = 'SANAD Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner', string='Contact', required=True, ondelete='restrict',
        tracking=True,
        help='Source of truth for the patient\'s name and contact details.')
    user_id = fields.Many2one(
        'res.users', string='Login User', ondelete='restrict', tracking=True,
        help='Odoo user account used by this patient to log in, if granted.')

    name = fields.Char(related='partner_id.name', string='Full Name', store=True, readonly=True)
    phone = fields.Char(related='partner_id.phone', string='Phone', readonly=True)
    email = fields.Char(related='partner_id.email', string='Email', readonly=True)
    address = fields.Text(compute='_compute_address', string='Address')

    birth_date = fields.Date(string='Date of Birth', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age')

    blood_group = fields.Selection([
        ('a_pos', 'A+'), ('a_neg', 'A-'),
        ('b_pos', 'B+'), ('b_neg', 'B-'),
        ('ab_pos', 'AB+'), ('ab_neg', 'AB-'),
        ('o_pos', 'O+'), ('o_neg', 'O-'),
        ('unknown', 'Unknown'),
    ], string='Blood Group', default='unknown')
    allergies = fields.Text(string='Allergies')
    chronic_diseases = fields.Text(string='Chronic Diseases')
    medical_notes = fields.Text(string='Medical Notes')

    emergency_contact_name = fields.Char(string='Emergency Contact Name')
    emergency_contact_phone = fields.Char(string='Emergency Contact Phone')
    emergency_contact_relation = fields.Char(string='Relationship')

    care_rel_ids = fields.One2many(
        'sanad.patient.doctor.rel', 'patient_id', string='Care Relationships')
    doctor_ids = fields.Many2many(
        'sanad.doctor', string='Treating Doctors',
        compute='_compute_doctor_ids',
        help='Doctors currently in an active care relationship with this patient.')

    active = fields.Boolean(default=True)
    created_date = fields.Datetime(
        string='Registration Date', default=fields.Datetime.now, readonly=True)

    # Odoo 19: _sql_constraints removed - use models.Constraint attributes.
    _partner_uniq = models.Constraint(
        'unique(partner_id)',
        'This contact is already registered as a patient.',
    )

    @api.depends('partner_id')
    def _compute_address(self):
        for patient in self:
            partner = patient.partner_id
            parts = [partner.street, partner.street2, partner.city,
                     partner.state_id.name, partner.zip, partner.country_id.name]
            patient.address = ', '.join(p for p in parts if p) or False

    @api.depends('birth_date')
    def _compute_age(self):
        today = fields.Date.today()
        for patient in self:
            if patient.birth_date:
                years = today.year - patient.birth_date.year
                if (today.month, today.day) < (patient.birth_date.month, patient.birth_date.day):
                    years -= 1
                patient.age = years
            else:
                patient.age = 0

    @api.depends('care_rel_ids.active', 'care_rel_ids.doctor_id')
    def _compute_doctor_ids(self):
        for patient in self:
            active_rels = patient.care_rel_ids.filtered(lambda r: r.active)
            patient.doctor_ids = active_rels.mapped('doctor_id')

    @api.constrains('user_id')
    def _check_user_not_reused(self):
        for patient in self:
            if patient.user_id:
                other = self.search([
                    ('user_id', '=', patient.user_id.id),
                    ('id', '!=', patient.id),
                ], limit=1)
                if other:
                    raise ValidationError(
                        'This user account is already linked to another '
                        'patient profile (%s).' % other.display_name)

    def name_get(self):
        result = []
        for patient in self:
            result.append((patient.id, patient.partner_id.name or 'Unnamed Patient'))
        return result
