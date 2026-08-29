# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadLaboratoryOrg(models.Model):
    """A laboratory organization.

    Named 'laboratory_org' (model: sanad.laboratory.org) rather than
    'sanad.laboratory' to avoid collision with the analysis-request
    workflow model that will be introduced in sanad_laboratory (Phase 4).
    This model represents the organization itself; the Phase 4 model
    represents individual analysis requests sent to it.
    """
    _name = 'sanad.laboratory.org'
    _description = 'SANAD Laboratory Organization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Laboratory Name', required=True, tracking=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    active = fields.Boolean(default=True)
