# -*- coding: utf-8 -*-
from odoo import fields, models


class SanadMedicalSpecialty(models.Model):
    """Catalog of medical specialties assignable to doctors.

    Kept as its own model (rather than a Selection field) so the list
    can be extended by administrators without a code change, and so it
    can later carry translations or metadata (e.g. required for AI
    routing rules) without a schema migration.
    """
    _name = 'sanad.medical.specialty'
    _description = 'SANAD Medical Specialty'
    _order = 'name'

    name = fields.Char(string='Specialty', required=True, translate=True)
    code = fields.Char(string='Code', help='Short internal code, e.g. CARDIO, PEDIA.')
    active = fields.Boolean(default=True)

    # Odoo 19: _sql_constraints removed - use models.Constraint attributes.
    _name_uniq = models.Constraint(
        'unique(name)',
        'This specialty already exists.',
    )
