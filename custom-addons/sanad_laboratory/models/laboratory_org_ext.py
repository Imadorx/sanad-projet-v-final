# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadLaboratoryOrgExtension(models.Model):
    """Extends sanad.laboratory.org (sanad_core) with staff assignment,
    mirroring the pattern used for sanad.pharmacy.org in sanad_medical.
    Needed to scope which lab requests a laboratory user can see
    (PRD 14.3: Laboratory can view assigned analysis requests only)."""
    _inherit = 'sanad.laboratory.org'

    user_ids = fields.Many2many(
        'res.users', string='Laboratory Staff',
        help='Users who log in as staff of this laboratory. Used to scope '
             'which analysis requests they can see and process.')
