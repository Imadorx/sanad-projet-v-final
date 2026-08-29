# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadPharmacyOrgExtension(models.Model):
    """Extends sanad.pharmacy.org (defined in sanad_core) with the user
    assignment needed to scope prescription visibility per pharmacy
    (PRD 14.3: "Pharmacy can view prescriptions assigned to pharmacy").

    This field lives here rather than in sanad_core because it is only
    meaningful once sanad.prescription exists to be scoped - sanad_core
    has no concept of "assigned prescriptions" and shouldn't need to.
    """
    _inherit = 'sanad.pharmacy.org'

    user_ids = fields.Many2many(
        'res.users', string='Pharmacy Staff',
        domain=[('groups_id', 'in', [])],  # left open; group filter is UI-side via the Pharmacy security group
        help='Users who log in as staff of this pharmacy. Used to scope '
             'which prescriptions they can see and process.')
