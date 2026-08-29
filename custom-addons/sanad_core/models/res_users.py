# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    """SANAD role helpers for res.users."""

    _inherit = 'res.users'

    sanad_role_ids = fields.Many2many(
        'res.groups',
        string='SANAD Roles',
        compute='_compute_sanad_role_ids',
        readonly=True,
        help='SANAD-specific security groups this user currently belongs to.',
    )

    def _compute_sanad_role_ids(self):
        admin_group = self.env.ref(
            'sanad_core.group_sanad_admin',
            raise_if_not_found=False,
        )
        doctor_group = self.env.ref(
            'sanad_core.group_sanad_doctor',
            raise_if_not_found=False,
        )
        patient_group = self.env.ref(
            'sanad_core.group_sanad_patient',
            raise_if_not_found=False,
        )
        laboratory_group = self.env.ref(
            'sanad_core.group_sanad_laboratory',
            raise_if_not_found=False,
        )
        pharmacy_group = self.env.ref(
            'sanad_core.group_sanad_pharmacy',
            raise_if_not_found=False,
        )

        sanad_groups = self.env['res.groups'].browse([
            group.id
            for group in (
                admin_group,
                doctor_group,
                patient_group,
                laboratory_group,
                pharmacy_group,
            )
            if group
        ])

        for user in self:
            user.sanad_role_ids = user.group_ids & sanad_groups

    def has_sanad_role(self, xml_id):
        """Check whether the current user belongs to a SANAD role group."""
        self.ensure_one()

        group = self.env.ref(
            xml_id,
            raise_if_not_found=False,
        )

        return bool(group) and group in self.group_ids