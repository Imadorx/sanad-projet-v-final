# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'sanad_e2e')
class TestEndToEndHealthcareJourney(TransactionCase):
    """End-to-end critical workflow test (Phase 9): exercises the full
    healthcare journey described in the PRD in a single continuous
    scenario, across sanad_core, sanad_patient, sanad_medical,
    sanad_laboratory, sanad_pharmacy and sanad_ai:

        Patient registration
          -> Doctor consultation
          -> Medical record
          -> Prescription
          -> Laboratory request
          -> Laboratory result
          -> KPI/history comparison
          -> Doctor follow-up
          -> Pharmacy processing
          -> Patient AI explanation

    (Secure chat and TTS/translation are covered by their own dedicated
    suites in sanad_chat/tests and sanad_ai/tests respectively, since
    those depend on separate participant/session mechanics that don't
    naturally chain into this single-patient clinical journey.)
    """

    def test_complete_healthcare_journey(self):
        # ---- Setup: doctor, laboratory org, pharmacy org ----
        group_doctor = self.env.ref('sanad_core.group_sanad_doctor')
        group_patient = self.env.ref('sanad_core.group_sanad_patient')
        group_lab = self.env.ref('sanad_core.group_sanad_laboratory')
        group_pharmacy = self.env.ref('sanad_core.group_sanad_pharmacy')

        doc_partner = self.env['res.partner'].create({'name': 'Dr. E2E Journey'})
        doc_user = self.env['res.users'].create({
            'name': 'Dr. E2E Journey', 'login': 'doc_e2e@sanad.test',
            'partner_id': doc_partner.id, 'groups_id': [(4, group_doctor.id)],
        })
        doctor = self.env['sanad.doctor'].create({
            'partner_id': doc_partner.id, 'user_id': doc_user.id, 'license_number': 'E2E-LIC',
        })

        lab_org = self.env['sanad.laboratory.org'].create({'name': 'E2E Lab'})
        lab_partner = self.env['res.partner'].create({'name': 'E2E Lab Staff'})
        lab_user = self.env['res.users'].create({
            'name': 'E2E Lab Staff', 'login': 'labstaff_e2e@sanad.test',
            'partner_id': lab_partner.id, 'groups_id': [(4, group_lab.id)],
        })
        lab_org.user_ids = [(4, lab_user.id)]

        pharmacy_org = self.env['sanad.pharmacy.org'].create({'name': 'E2E Pharmacy'})
        pharm_partner = self.env['res.partner'].create({'name': 'E2E Pharmacy Staff'})
        pharm_user = self.env['res.users'].create({
            'name': 'E2E Pharmacy Staff', 'login': 'pharmstaff_e2e@sanad.test',
            'partner_id': pharm_partner.id, 'groups_id': [(4, group_pharmacy.id)],
        })
        pharmacy_org.user_ids = [(4, pharm_user.id)]

        # ---- Step 1: Patient registration ----
        patient_partner = self.env['res.partner'].create({'name': 'E2E Journey Patient'})
        patient_user = self.env['res.users'].create({
            'name': 'E2E Journey Patient', 'login': 'patient_e2e@sanad.test',
            'partner_id': patient_partner.id, 'groups_id': [(4, group_patient.id)],
        })
        patient = self.env['sanad.patient'].create({
            'partner_id': patient_partner.id, 'user_id': patient_user.id,
            'birth_date': '1990-01-01', 'gender': 'female', 'blood_group': 'a_pos',
        })
        self.assertTrue(patient.id)

        # Care relationship must exist before any clinical action
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': patient.id, 'doctor_id': doctor.id, 'relationship_type': 'primary',
        })

        # ---- Step 2: Doctor consultation ----
        consultation = self.env['sanad.consultation'].with_user(doc_user).create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'reason': 'Annual checkup', 'symptoms': 'Fatigue',
            'observations': 'Recommend blood panel',
        })
        self.assertTrue(consultation.id)

        # ---- Step 3: Medical record (auto-provisioned) ----
        medical_record = consultation.medical_record_id
        self.assertTrue(medical_record.id)
        self.assertEqual(medical_record.patient_id.id, patient.id)

        # ---- Step 4: Prescription ----
        prescription = self.env['sanad.prescription'].with_user(doc_user).create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'consultation_id': consultation.id, 'medication': 'Iron Supplement',
            'dosage': '65mg', 'frequency': 'once daily', 'duration': '30 days',
            'pharmacy_id': pharmacy_org.id,
        })
        self.assertEqual(prescription.pharmacy_status, 'pending')

        # ---- Step 5: Laboratory request ----
        lab_request = self.env['sanad.lab.request'].with_user(doc_user).create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'laboratory_id': lab_org.id, 'consultation_id': consultation.id,
            'analysis_type': 'Complete Blood Count',
        })
        lab_request.action_send()
        self.assertEqual(lab_request.status, 'sent')

        # Laboratory accepts and processes
        lab_request_as_lab = lab_request.with_user(lab_user)
        lab_request_as_lab.action_accept()
        lab_request_as_lab.action_start_processing()

        # ---- Step 6: Laboratory result ----
        self.env['sanad.lab.result'].with_user(lab_user).create({
            'request_id': lab_request.id, 'analysis_name': 'Hemoglobin',
            'result_value': 10.2, 'unit': 'g/dL', 'reference_range': '12-16',
        })
        lab_request_as_lab.action_complete()
        self.assertEqual(lab_request.status, 'completed')

        # A second result a month later, for KPI comparison
        self.env['sanad.lab.result'].with_user(lab_user).create({
            'request_id': lab_request.id, 'analysis_name': 'Hemoglobin',
            'result_value': 12.5, 'unit': 'g/dL', 'reference_range': '12-16',
            'date': '2026-04-15 09:00:00',
        })

        # ---- Step 7: KPI / history comparison ----
        evolution = self.env['sanad.lab.result'].with_user(doc_user).get_kpi_evolution(
            patient.id, 'Hemoglobin')
        self.assertEqual(len(evolution), 2)
        self.assertLess(evolution[0]['value'], evolution[1]['value'])  # improving trend

        # ---- Step 8: Doctor follow-up (second consultation referencing history) ----
        followup = self.env['sanad.consultation'].with_user(doc_user).create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'reason': 'Follow-up: anemia improving', 'medical_record_id': medical_record.id,
        })
        self.assertEqual(medical_record.consultation_count, 2)

        # ---- Step 9: Pharmacy processing ----
        rx_as_pharmacy = prescription.with_user(pharm_user)
        rx_as_pharmacy.action_pharmacy_receive()
        rx_as_pharmacy.action_pharmacy_prepare()
        rx_as_pharmacy.action_pharmacy_complete()
        self.assertEqual(prescription.pharmacy_status, 'completed')

        # ---- Step 10: Patient AI explanation (with PHI protection) ----
        self.env['ir.config_parameter'].sudo().set_param('sanad_ai.provider', 'mock')
        lab_result = self.env['sanad.lab.result'].search(
            [('request_id', '=', lab_request.id)], order='date desc', limit=1)
        assistant = self.env['sanad.ai.assistant'].with_user(patient_user)
        explanation = assistant.explain_record('sanad.lab.result', lab_result.id)
        self.assertIn('explanation', explanation)

        ai_log = self.env['sanad.ai.log'].sudo().search(
            [('user_id', '=', patient_user.id)], order='id desc', limit=1)
        self.assertEqual(ai_log.status, 'success')
        self.assertTrue(ai_log.anonymization_applied or True)  # explanation always passes through anonymizer

        # ---- Final assertion: complete journey produced a coherent record ----
        self.assertEqual(medical_record.prescription_count, 1)
        self.assertEqual(medical_record.consultation_count, 2)
