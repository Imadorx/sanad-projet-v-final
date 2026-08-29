# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'sanad_ai')
class TestAiAssistantAuthorization(TransactionCase):
    """AI authorization + audit logging tests (Phase 8): unauthorized
    data access must be blocked BEFORE any provider call, and every
    outcome (success/failed/blocked) must be logged to sanad.ai.log."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        group_patient = cls.env.ref('sanad_core.group_sanad_patient')

        partner_doc = cls.env['res.partner'].create({'name': 'Dr. AI Test'})
        cls.user_doc = cls.env['res.users'].create({
            'name': 'Dr. AI Test', 'login': 'doc_aitest@sanad.test',
            'partner_id': partner_doc.id, 'groups_id': [(4, group_doctor.id)],
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': partner_doc.id, 'user_id': cls.user_doc.id, 'license_number': 'AI-TEST-LIC',
        })

        # Patient WITH an active relationship to the doctor
        partner_authorized = cls.env['res.partner'].create({'name': 'Authorized AI Patient'})
        cls.patient_authorized = cls.env['sanad.patient'].create({'partner_id': partner_authorized.id})
        cls.env['sanad.patient.doctor.rel'].create({
            'patient_id': cls.patient_authorized.id, 'doctor_id': cls.doctor.id,
            'relationship_type': 'primary',
        })

        # Patient with NO relationship to the doctor
        partner_unauthorized = cls.env['res.partner'].create({'name': 'Unauthorized AI Patient'})
        cls.patient_unauthorized = cls.env['sanad.patient'].create({'partner_id': partner_unauthorized.id})

        # Force the mock provider explicitly (safe default, no network calls)
        cls.env['ir.config_parameter'].sudo().set_param('sanad_ai.provider', 'mock')

    def test_search_blocked_for_unauthorized_patient(self):
        """A doctor with no care relationship to a patient must be
        blocked from AI-searching that patient's data, and the block
        must be logged BEFORE any provider call."""
        assistant = self.env['sanad.ai.assistant'].with_user(self.user_doc)
        with self.assertRaises(AccessError):
            assistant.authorized_search('glucose', patient_id=self.patient_unauthorized.id)

        blocked_logs = self.env['sanad.ai.log'].sudo().search([
            ('user_id', '=', self.user_doc.id), ('status', '=', 'blocked'),
        ])
        self.assertTrue(blocked_logs)

    def test_search_succeeds_for_authorized_patient(self):
        self.env['sanad.consultation'].create({
            'patient_id': self.patient_authorized.id, 'doctor_id': self.doctor.id,
            'reason': 'Routine glucose check',
        })
        assistant = self.env['sanad.ai.assistant'].with_user(self.user_doc)
        result = assistant.authorized_search('glucose', patient_id=self.patient_authorized.id)
        self.assertIn('summary', result)

        success_logs = self.env['sanad.ai.log'].sudo().search([
            ('user_id', '=', self.user_doc.id), ('status', '=', 'success'),
            ('request_type', '=', 'search'),
        ])
        self.assertTrue(success_logs)

    def test_explain_rejects_disallowed_model(self):
        """Only sanad.consultation and sanad.lab.result are valid
        explain() targets - anything else must be rejected outright,
        preventing the AI from being pointed at arbitrary models."""
        assistant = self.env['sanad.ai.assistant'].with_user(self.user_doc)
        from odoo.exceptions import UserError
        with self.assertRaises(UserError):
            assistant.explain_record('res.partner', self.doctor.partner_id.id)

    def test_every_ai_log_has_required_audit_fields(self):
        self.env['sanad.consultation'].create({
            'patient_id': self.patient_authorized.id, 'doctor_id': self.doctor.id,
            'reason': 'Audit field test',
        })
        assistant = self.env['sanad.ai.assistant'].with_user(self.user_doc)
        assistant.authorized_search('audit', patient_id=self.patient_authorized.id)
        log = self.env['sanad.ai.log'].sudo().search(
            [('user_id', '=', self.user_doc.id)], order='id desc', limit=1)
        self.assertTrue(log.timestamp)
        self.assertIn(log.status, ('success', 'failed', 'blocked'))
        self.assertEqual(log.request_type, 'search')

    def test_ai_log_not_writable_by_doctor_group(self):
        """Per the Phase 1 design, no security group has direct write
        access to sanad.ai.log - only sudo() from sanad_ai code can
        write to it. Verifies a doctor cannot fabricate an audit entry."""
        with self.assertRaises(AccessError):
            self.env['sanad.ai.log'].with_user(self.user_doc).create({
                'user_id': self.user_doc.id, 'request_type': 'search',
                'status': 'success',
            })
