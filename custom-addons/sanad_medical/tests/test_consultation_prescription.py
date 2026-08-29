# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'sanad_medical')
class TestConsultationPrescription(TransactionCase):
    """Defense-in-depth tests (Phase 3): consultations and prescriptions
    must be blocked at the ORM constraint layer, not just hidden by
    record rules, when no active care relationship exists."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')

        cls.partner_doc = cls.env['res.partner'].create({'name': 'Dr. Medical Test'})
        cls.user_doc = cls.env['res.users'].create({
            'name': 'Dr. Medical Test', 'login': 'doc_medtest@sanad.test',
            'partner_id': cls.partner_doc.id, 'groups_id': [(4, cls.group_doctor.id)],
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': cls.partner_doc.id, 'user_id': cls.user_doc.id,
            'license_number': 'MED-TEST-LIC',
        })

        cls.partner_patient = cls.env['res.partner'].create({'name': 'Med Test Patient'})
        cls.patient = cls.env['sanad.patient'].create({'partner_id': cls.partner_patient.id})

    def test_consultation_blocked_without_care_relationship(self):
        """No sanad.patient.doctor.rel exists yet between doctor and
        patient - creating a consultation must raise, proving the
        @api.constrains check works independently of record rules."""
        with self.assertRaises(ValidationError):
            self.env['sanad.consultation'].create({
                'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
                'reason': 'Should be blocked',
            })

    def test_consultation_allowed_with_active_relationship(self):
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'relationship_type': 'primary',
        })
        consultation = self.env['sanad.consultation'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'reason': 'Allowed consultation',
        })
        self.assertTrue(consultation.id)
        # Medical record must be auto-provisioned on first consultation
        self.assertTrue(consultation.medical_record_id)

    def test_prescription_blocked_without_care_relationship(self):
        with self.assertRaises(ValidationError):
            self.env['sanad.prescription'].create({
                'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
                'medication': 'Test Med', 'dosage': '500mg',
                'frequency': 'once daily', 'duration': '5 days',
            })

    def test_prescription_allowed_with_active_relationship(self):
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'relationship_type': 'primary',
        })
        prescription = self.env['sanad.prescription'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'medication': 'Test Med', 'dosage': '500mg',
            'frequency': 'once daily', 'duration': '5 days',
        })
        self.assertEqual(prescription.pharmacy_status, 'pending')

    def test_medical_record_is_idempotent_per_patient(self):
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'relationship_type': 'primary',
        })
        c1 = self.env['sanad.consultation'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id, 'reason': 'Visit 1',
        })
        c2 = self.env['sanad.consultation'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id, 'reason': 'Visit 2',
        })
        self.assertEqual(c1.medical_record_id.id, c2.medical_record_id.id)
        self.assertEqual(c1.medical_record_id.consultation_count, 2)
