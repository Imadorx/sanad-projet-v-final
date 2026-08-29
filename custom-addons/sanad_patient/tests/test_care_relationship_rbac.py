# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, AccessError


@tagged('post_install', '-at_install', 'sanad_rbac')
class TestCareRelationshipRbac(TransactionCase):
    """Core RBAC backbone tests (Phase 2): the sanad.patient.doctor.rel
    model is what every clinical model's access control keys off, so
    this suite is the single most important RBAC test in the project."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        cls.group_patient = cls.env.ref('sanad_core.group_sanad_patient')

        # Doctor A - assigned to Patient 1
        cls.partner_doc_a = cls.env['res.partner'].create({'name': 'Dr. A'})
        cls.user_doc_a = cls.env['res.users'].create({
            'name': 'Dr. A', 'login': 'doc_a@sanad.test', 'partner_id': cls.partner_doc_a.id,
            'groups_id': [(4, cls.group_doctor.id)],
        })
        cls.doctor_a = cls.env['sanad.doctor'].create({
            'partner_id': cls.partner_doc_a.id, 'user_id': cls.user_doc_a.id,
            'license_number': 'RBAC-LIC-A',
        })

        # Doctor B - NOT assigned to Patient 1
        cls.partner_doc_b = cls.env['res.partner'].create({'name': 'Dr. B'})
        cls.user_doc_b = cls.env['res.users'].create({
            'name': 'Dr. B', 'login': 'doc_b@sanad.test', 'partner_id': cls.partner_doc_b.id,
            'groups_id': [(4, cls.group_doctor.id)],
        })
        cls.doctor_b = cls.env['sanad.doctor'].create({
            'partner_id': cls.partner_doc_b.id, 'user_id': cls.user_doc_b.id,
            'license_number': 'RBAC-LIC-B',
        })

        # Patient 1 - only Doctor A has an active care relationship
        cls.partner_patient = cls.env['res.partner'].create({'name': 'Patient One'})
        cls.user_patient = cls.env['res.users'].create({
            'name': 'Patient One', 'login': 'patient1@sanad.test',
            'partner_id': cls.partner_patient.id, 'groups_id': [(4, cls.group_patient.id)],
        })
        cls.patient = cls.env['sanad.patient'].create({
            'partner_id': cls.partner_patient.id, 'user_id': cls.user_patient.id,
        })
        cls.env['sanad.patient.doctor.rel'].create({
            'patient_id': cls.patient.id, 'doctor_id': cls.doctor_a.id,
            'relationship_type': 'primary',
        })

    def test_doctor_with_active_relationship_sees_patient(self):
        patients = self.env['sanad.patient'].with_user(self.user_doc_a).search([])
        self.assertIn(self.patient, patients)

    def test_doctor_without_relationship_cannot_see_patient(self):
        """Doctor B has no care relationship with Patient 1 - the
        record-rule domain must exclude the patient entirely from
        Doctor B's search results (not raise, just not appear -
        matching ir.rule semantics)."""
        patients = self.env['sanad.patient'].with_user(self.user_doc_b).search([])
        self.assertNotIn(self.patient, patients)

    def test_patient_sees_only_own_record(self):
        other_partner = self.env['res.partner'].create({'name': 'Patient Two'})
        other_user = self.env['res.users'].create({
            'name': 'Patient Two', 'login': 'patient2@sanad.test',
            'partner_id': other_partner.id, 'groups_id': [(4, self.group_patient.id)],
        })
        self.env['sanad.patient'].create({
            'partner_id': other_partner.id, 'user_id': other_user.id,
        })
        own_visible = self.env['sanad.patient'].with_user(self.user_patient).search([])
        self.assertEqual(len(own_visible), 1)
        self.assertEqual(own_visible.id, self.patient.id)

    def test_care_relationship_requires_valid_dates(self):
        with self.assertRaises(ValidationError):
            self.env['sanad.patient.doctor.rel'].create({
                'patient_id': self.patient.id, 'doctor_id': self.doctor_b.id,
                'relationship_type': 'consulting',
                'start_date': '2026-06-01', 'end_date': '2026-01-01',
            })

    def test_ended_relationship_deactivates_access(self):
        rel = self.env['sanad.patient.doctor.rel'].search([
            ('patient_id', '=', self.patient.id), ('doctor_id', '=', self.doctor_a.id),
        ])
        rel.write({'end_date': '2020-01-01'})  # past date
        self.assertFalse(rel.active)
        patients = self.env['sanad.patient'].with_user(self.user_doc_a).search([])
        self.assertNotIn(self.patient, patients)
