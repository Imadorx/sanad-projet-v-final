# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'sanad_chat')
class TestChatPairing(TransactionCase):
    """Server-side pairing enforcement tests (Phase 6): only PRD-allowed
    conversation types are permitted, and doctor-patient chats require
    an active care relationship - verified independent of the UI."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        group_doctor = cls.env.ref('sanad_core.group_sanad_doctor')
        group_patient = cls.env.ref('sanad_core.group_sanad_patient')

        partner_doc = cls.env['res.partner'].create({'name': 'Dr. Chat Test'})
        cls.user_doc = cls.env['res.users'].create({
            'name': 'Dr. Chat Test', 'login': 'doc_chattest@sanad.test',
            'partner_id': partner_doc.id, 'groups_id': [(4, group_doctor.id)],
        })
        cls.doctor = cls.env['sanad.doctor'].create({
            'partner_id': partner_doc.id, 'user_id': cls.user_doc.id, 'license_number': 'CHAT-TEST-LIC',
        })

        partner_patient = cls.env['res.partner'].create({'name': 'Chat Test Patient'})
        cls.user_patient = cls.env['res.users'].create({
            'name': 'Chat Test Patient', 'login': 'patient_chattest@sanad.test',
            'partner_id': partner_patient.id, 'groups_id': [(4, group_patient.id)],
        })
        cls.patient = cls.env['sanad.patient'].create({
            'partner_id': partner_patient.id, 'user_id': cls.user_patient.id,
        })

        # A second, unrelated patient with NO care relationship to the doctor
        partner_unrelated = cls.env['res.partner'].create({'name': 'Unrelated Patient'})
        cls.user_unrelated = cls.env['res.users'].create({
            'name': 'Unrelated Patient', 'login': 'unrelated_chattest@sanad.test',
            'partner_id': partner_unrelated.id, 'groups_id': [(4, group_patient.id)],
        })
        cls.env['sanad.patient'].create({
            'partner_id': partner_unrelated.id, 'user_id': cls.user_unrelated.id,
        })

    def test_conversation_requires_exactly_two_participants(self):
        with self.assertRaises(ValidationError):
            self.env['sanad.chat.conversation'].create({
                'participant_ids': [(6, 0, [self.user_doc.id])],
                'conversation_type': 'doctor_patient',
            })

    def test_doctor_patient_chat_blocked_without_care_relationship(self):
        with self.assertRaises(ValidationError):
            self.env['sanad.chat.conversation'].create({
                'participant_ids': [(6, 0, [self.user_doc.id, self.user_patient.id])],
                'conversation_type': 'doctor_patient',
            })

    def test_doctor_patient_chat_allowed_with_active_relationship(self):
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id, 'relationship_type': 'primary',
        })
        conv = self.env['sanad.chat.conversation'].create({
            'participant_ids': [(6, 0, [self.user_doc.id, self.user_patient.id])],
            'conversation_type': 'doctor_patient',
        })
        self.assertEqual(conv.patient_id.id, self.patient.id)

    def test_unrelated_patient_cannot_chat_with_doctor(self):
        """Even though both parties are valid SANAD users, no care
        relationship exists, so the pairing must be rejected."""
        with self.assertRaises(ValidationError):
            self.env['sanad.chat.conversation'].create({
                'participant_ids': [(6, 0, [self.user_doc.id, self.user_unrelated.id])],
                'conversation_type': 'doctor_patient',
            })

    def test_participant_only_visibility(self):
        self.env['sanad.patient.doctor.rel'].create({
            'patient_id': self.patient.id, 'doctor_id': self.doctor.id, 'relationship_type': 'primary',
        })
        conv = self.env['sanad.chat.conversation'].create({
            'participant_ids': [(6, 0, [self.user_doc.id, self.user_patient.id])],
            'conversation_type': 'doctor_patient',
        })
        visible_to_unrelated = self.env['sanad.chat.conversation'].with_user(
            self.user_unrelated).search([])
        self.assertNotIn(conv, visible_to_unrelated)
        visible_to_doctor = self.env['sanad.chat.conversation'].with_user(self.user_doc).search([])
        self.assertIn(conv, visible_to_doctor)
