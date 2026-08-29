# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.sanad_ai.services.anonymizer import (
    anonymize_text, build_replacement_map, anonymize_patient_summary,
)


@tagged('post_install', '-at_install', 'sanad_ai')
class TestAnonymization(TransactionCase):
    """PHI anonymization tests (Phase 8) - the mandatory layer between
    any patient data and an external AI provider."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env['res.partner'].create({
            'name': 'Anon Test Patient', 'phone': '+212611112222', 'email': 'anontest@sanad.test',
        })
        cls.patient = cls.env['sanad.patient'].create({
            'partner_id': partner.id, 'birth_date': '1985-04-12', 'gender': 'male',
            'blood_group': 'o_pos', 'allergies': 'Penicillin',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': '+212699998888',
        })
        doc_partner = cls.env['res.partner'].create({
            'name': 'Dr. Anon Test', 'phone': '+212633334444', 'email': 'doctest@sanad.test',
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': doc_partner.id, 'license_number': 'ANON-TEST-LIC',
        })

    def test_patient_identifiers_stripped_from_text(self):
        replacement_map = build_replacement_map(patient=self.patient, doctor=self.doctor)
        raw = f'Patient {self.patient.name} was treated by {self.doctor.name}.'
        anon, applied = anonymize_text(raw, replacement_map)
        self.assertTrue(applied)
        self.assertNotIn(self.patient.name, anon)
        self.assertNotIn(self.doctor.name, anon)
        self.assertIn('[PATIENT_NAME]', anon)
        self.assertIn('[DOCTOR_NAME]', anon)

    def test_patient_summary_never_includes_identity(self):
        """anonymize_patient_summary must return demographic categories
        only - name/phone/email/address must never appear as keys."""
        summary = anonymize_patient_summary(self.patient)
        forbidden_keys = {'name', 'phone', 'email', 'address',
                           'emergency_contact_name', 'emergency_contact_phone'}
        self.assertFalse(forbidden_keys & set(summary.keys()))
        self.assertIn('age', summary)
        self.assertIn('blood_group', summary)

    def test_unmapped_email_still_redacted_by_pattern(self):
        """An email not in the known-identifier map (e.g. typed by a
        user in free text) must still be caught by the pattern sweep."""
        text = 'Please contact stranger@example.com for follow-up.'
        anon, applied = anonymize_text(text)
        self.assertTrue(applied)
        self.assertNotIn('stranger@example.com', anon)
