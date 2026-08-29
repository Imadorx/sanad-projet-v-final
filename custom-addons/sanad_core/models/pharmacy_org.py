# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadPharmacyOrg(models.Model):
    """A pharmacy organization."""
    _name = 'sanad.pharmacy.org'
    _description = 'SANAD Pharmacy Organization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Pharmacy Name', required=True, tracking=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    active = fields.Boolean(default=True)
