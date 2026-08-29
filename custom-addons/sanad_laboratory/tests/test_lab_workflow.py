# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'sanad_laboratory')
class TestLabWorkflow(TransactionCase):
    """Status workflow tests (Phase 4): Draft->Sent->Accepted->
    Processing->Completed/Cancelled, plus KPI evolution."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        partner_doc = cls.env['res.partner'].create({'name': 'Dr. Lab Test'})
        cls.user_doc = cls.env['res.users'].create({
            'name': 'Dr. Lab Test', 'login': 'doc_labtest@sanad.test',
            'partner_id': partner_doc.id, 'groups_id': [(4, cls.group_doctor.id)],
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': partner_doc.id, 'user_id': cls.user_doc.id, 'license_number': 'LAB-TEST-LIC',
        })
        partner_patient = cls.env['res.partner'].create({'name': 'Lab Test Patient'})
        cls.patient = cls.env['sanad.patient'].create({'partner_id': partner_patient.id})
        cls.env['sanad.patient.doctor.rel'].create({
            'patient_id': cls.patient.id, 'doctor_id': cls.doctor.id, 'relationship_type': 'primary',
        })
        cls.lab_org = cls.env['sanad.laboratory.org'].create({'name': 'Test Lab'})

    def test_request_starts_as_draft(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'CBC',
        })
        self.assertEqual(req.status, 'draft')

    def test_full_workflow_transition(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'CBC',
        })
        req.action_send()
        self.assertEqual(req.status, 'sent')
        req.action_accept()
        self.assertEqual(req.status, 'accepted')
        req.action_start_processing()
        self.assertEqual(req.status, 'processing')
        self.env['sanad.lab.result'].create({
            'request_id': req.id, 'analysis_name': 'WBC', 'result_value': 6.5, 'unit': 'K/uL',
        })
        req.action_complete()
        self.assertEqual(req.status, 'completed')

    def test_cannot_complete_without_results(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'CBC',
        })
        req.action_send(); req.action_accept(); req.action_start_processing()
        with self.assertRaises(ValidationError):
            req.action_complete()

    def test_cannot_skip_workflow_steps(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'CBC',
        })
        with self.assertRaises(ValidationError):
            req.action_accept()  # cannot accept a draft directly

    def test_completed_request_cannot_be_cancelled(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'CBC',
        })
        req.action_send(); req.action_accept(); req.action_start_processing()
        self.env['sanad.lab.result'].create({
            'request_id': req.id, 'analysis_name': 'WBC', 'result_value': 6.5,
        })
        req.action_complete()
        with self.assertRaises(ValidationError):
            req.action_cancel()

    def test_kpi_evolution_returns_chronological_series(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'Glucose Panel',
        })
        self.env['sanad.lab.result'].create({
            'request_id': req.id, 'analysis_name': 'Glucose', 'result_value': 120,
            'unit': 'mg/dL', 'date': '2026-01-15 09:00:00',
        })
        self.env['sanad.lab.result'].create({
            'request_id': req.id, 'analysis_name': 'Glucose', 'result_value': 105,
            'unit': 'mg/dL', 'date': '2026-03-15 09:00:00',
        })
        evolution = self.env['sanad.lab.result'].get_kpi_evolution(self.patient.id, 'Glucose')
        self.assertEqual(len(evolution), 2)
        self.assertEqual(evolution[0]['value'], 120)
        self.assertEqual(evolution[1]['value'], 105)

    def test_out_of_range_detection(self):
        req = self.env['sanad.lab.request'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id,
            'laboratory_id': self.lab_org.id, 'analysis_type': 'Glucose Panel',
        })
        result = self.env['sanad.lab.result'].create({
            'request_id': req.id, 'analysis_name': 'Glucose', 'result_value': 250,
            'reference_range': '70-100',
        })
        self.assertTrue(result.is_out_of_range)
