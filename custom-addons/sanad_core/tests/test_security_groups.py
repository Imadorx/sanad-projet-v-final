# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'sanad_rbac')
class TestSanadSecurityGroups(TransactionCase):
    """RBAC foundation tests: multi-role support, group additivity,
    and the doctor model's identity-linkage constraints (Phase 1)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_admin = cls.env.ref('sanad_core.group_sanad_admin')
        cls.group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        cls.group_patient = cls.env.ref('sanad_core.group_sanad_patient')

        cls.partner = cls.env['res.partner'].create({'name': 'Test Multi-Role User'})
        cls.user = cls.env['res.users'].create({
            'name': 'Test Multi-Role User',
            'login': 'multirole_test@sanad.test',
            'partner_id': cls.partner.id,
        })

    def test_user_can_hold_multiple_sanad_roles(self):
        """A user can simultaneously be Doctor and Admin (PRD decision:
        multi-role support, no implied_ids chaining between roles)."""
        self.user.write({'groups_id': [(4, self.group_doctor.id), (4, self.group_admin.id)]})
        self.assertIn(self.group_doctor, self.user.groups_id)
        self.assertIn(self.group_admin, self.user.groups_id)

    def test_doctor_group_does_not_imply_patient_group(self):
        """Verifies roles are NOT chained via implied_ids - a Doctor
        does not automatically gain Patient group membership."""
        self.user.write({'groups_id': [(4, self.group_doctor.id)]})
        self.assertIn(self.group_doctor, self.user.groups_id)
        self.assertNotIn(self.group_patient, self.user.groups_id)

    def test_sanad_role_ids_computed_field(self):
        """res.users.sanad_role_ids reflects only SANAD-category groups."""
        self.user.write({'groups_id': [(4, self.group_doctor.id)]})
        self.assertIn(self.group_doctor, self.user.sanad_role_ids)
