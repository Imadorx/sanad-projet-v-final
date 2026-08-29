# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'sanad_pharmacy')
class TestPharmacyWorkflow(TransactionCase):
    """Prescription reception workflow tests (Phase 5):
    Pending -> Received -> Prepared -> Completed."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        group_pharmacy = cls.env.ref('sanad_core.group_sanad_pharmacy')

        partner_doc = cls.env['res.partner'].create({'name': 'Dr. Pharmacy Test'})
        user_doc = cls.env['res.users'].create({
            'name': 'Dr. Pharmacy Test', 'login': 'doc_pharmtest@sanad.test',
            'partner_id': partner_doc.id, 'groups_id': [(4, group_doctor.id)],
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': partner_doc.id, 'user_id': user_doc.id, 'license_number': 'PHARM-TEST-LIC',
        })
        partner_patient = cls.env['res.partner'].create({'name': 'Pharmacy Test Patient'})
        cls.patient = cls.env['sanad.patient'].create({'partner_id': partner_patient.id})
        cls.env['sanad.patient.doctor.rel'].create({
            'patient_id': cls.patient.id, 'doctor_id': cls.doctor.id, 'relationship_type': 'primary',
        })

        cls.pharmacy_org = cls.env['sanad.pharmacy.org'].create({'name': 'Test Pharmacy'})
        partner_pharm_staff = cls.env['res.partner'].create({'name': 'Pharmacy Staff'})
        cls.user_pharm = cls.env['res.users'].create({
            'name': 'Pharmacy Staff', 'login': 'pharmstaff@sanad.test',
            'partner_id': partner_pharm_staff.id, 'groups_id': [(4, group_pharmacy.id)],
        })
        cls.pharmacy_org.user_ids = [(4, cls.user_pharm.id)]

        cls.prescription = cls.env['sanad.prescription'].create({
            'patient_id': cls.patient.id, 'doctor_id': cls.doctor.id,
            'medication': 'Amoxicillin', 'dosage': '500mg', 'frequency': '3x daily',
            'duration': '7 days', 'pharmacy_id': cls.pharmacy_org.id,
        })

    def test_prescription_starts_pending(self):
        self.assertEqual(self.prescription.pharmacy_status, 'pending')

    def test_full_pharmacy_workflow(self):
        rx = self.prescription.with_user(self.user_pharm)
        rx.action_pharmacy_receive()
        self.assertEqual(rx.pharmacy_status, 'received')
        rx.action_pharmacy_prepare()
        self.assertEqual(rx.pharmacy_status, 'prepared')
        rx.action_pharmacy_complete()
        self.assertEqual(rx.pharmacy_status, 'completed')

    def test_cannot_skip_pharmacy_steps(self):
        rx = self.prescription.with_user(self.user_pharm)
        with self.assertRaises(ValidationError):
            rx.action_pharmacy_prepare()  # cannot prepare a pending prescription directly

    def test_pharmacy_staff_only_sees_own_org_prescriptions(self):
        other_pharmacy = self.env['sanad.pharmacy.org'].create({'name': 'Other Pharmacy'})
        other_partner = self.env['res.partner'].create({'name': 'Other Pharmacy Staff'})
        group_pharmacy = self.env.ref('sanad_core.group_sanad_pharmacy')
        other_user = self.env['res.users'].create({
            'name': 'Other Pharmacy Staff', 'login': 'otherpharm@sanad.test',
            'partner_id': other_partner.id, 'groups_id': [(4, group_pharmacy.id)],
        })
        other_pharmacy.user_ids = [(4, other_user.id)]

        visible_to_other = self.env['sanad.prescription'].with_user(other_user).search([])
        self.assertNotIn(self.prescription, visible_to_other)

        visible_to_own = self.env['sanad.prescription'].with_user(self.user_pharm).search([])
        self.assertIn(self.prescription, visible_to_own)
