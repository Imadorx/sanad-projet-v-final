# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SanadDoctor(models.Model):
    """Doctor professional profile.

    Identity (name, phone, email, address) is NOT stored here. It is
    sourced from res.partner (via partner_id) and, where a login is
    granted, from res.users (via user_id). This model only carries the
    healthcare-domain-specific professional information described in
    the PRD: specialty, license number, cabinet affiliation and
    professional background.

    Living in sanad_core (rather than sanad_medical) is deliberate:
    sanad_laboratory, sanad_pharmacy and sanad_chat all need to
    reference "doctor" without depending on the full sanad_medical
    module, so the model belongs at the foundation level.
    """
    _name = 'sanad.doctor'
    _description = 'SANAD Doctor Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner', string='Contact', required=True, ondelete='restrict',
        tracking=True,
        help='Source of truth for the doctor\'s name and contact details.')
    user_id = fields.Many2one(
        'res.users', string='Login User', ondelete='restrict', tracking=True,
        help='Odoo user account used by this doctor to log in. '
             'Optional at creation time, required before the doctor can '
             'be granted the Doctor security group.')

    # Convenience related fields for list/search views - never edited here,
    # always sourced live from partner_id so there is a single source of truth.
    name = fields.Char(related='partner_id.name', string='Full Name', store=True, readonly=True)
    phone = fields.Char(related='partner_id.phone', string='Phone', readonly=True)
    email = fields.Char(related='partner_id.email', string='Email', readonly=True)

    specialty_id = fields.Many2one(
        'sanad.medical.specialty', string='Specialty', tracking=True)
    license_number = fields.Char(
        string='License Number', required=True, tracking=True,
        help='Official medical license / registration number.')
    cabinet_id = fields.Many2one(
        'sanad.medical.cabinet', string='Medical Cabinet', tracking=True)
    professional_info = fields.Text(
        string='Professional Information',
        help='Qualifications, bio, years of experience, etc.')
    active = fields.Boolean(default=True)

    # Odoo 19: _sql_constraints removed - use models.Constraint attributes.
    _license_uniq = models.Constraint(
        'unique(license_number)',
        'This license number is already registered to another doctor.',
    )
    _partner_uniq = models.Constraint(
        'unique(partner_id)',
        'This contact is already registered as a doctor.',
    )

    @api.constrains('user_id')
    def _check_user_not_reused(self):
        for doctor in self:
            if doctor.user_id:
                other = self.search([
                    ('user_id', '=', doctor.user_id.id),
                    ('id', '!=', doctor.id),
                ], limit=1)
                if other:
                    raise ValidationError(
                        'This user account is already linked to another '
                        'doctor profile (%s).' % other.display_name)

    def name_get(self):
        result = []
        for doctor in self:
            label = doctor.partner_id.name or 'Unnamed'
            if doctor.specialty_id:
                label = '%s (%s)' % (label, doctor.specialty_id.name)
            result.append((doctor.id, label))
        return result
