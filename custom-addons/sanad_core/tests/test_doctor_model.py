# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from psycopg2.errors import UniqueViolation
from odoo.tools import mute_logger


@tagged('post_install', '-at_install', 'sanad_core')
class TestSanadDoctorModel(TransactionCase):
    """Identity-linkage integrity tests for sanad.doctor (Phase 1)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Dr. Test One'})
        cls.partner_2 = cls.env['res.partner'].create({'name': 'Dr. Test Two'})
        cls.user_1 = cls.env['res.users'].create({
            'name': 'Dr. Test One', 'login': 'dr1@sanad.test', 'partner_id': cls.partner_1.id,
        })

    def test_doctor_identity_sourced_from_partner(self):
        """name/phone/email on sanad.doctor must be related fields, not
        independently stored - editing the partner should reflect
        immediately on the doctor record."""
        self.partner_1.phone = '+212600000001'
        doctor = self.env['sanad.doctor'].create({
            'partner_id': self.partner_1.id,
            'license_number': 'TEST-LIC-001',
        })
        self.assertEqual(doctor.name, 'Dr. Test One')
        self.assertEqual(doctor.phone, '+212600000001')

    def test_duplicate_license_number_rejected(self):
        self.env['sanad.doctor'].create({
            'partner_id': self.partner_1.id, 'license_number': 'DUP-LIC-001',
        })
        with self.assertRaises(Exception), mute_logger('odoo.sql_db'):
            self.env['sanad.doctor'].create({
                'partner_id': self.partner_2.id, 'license_number': 'DUP-LIC-001',
            })

    def test_same_partner_cannot_be_two_doctors(self):
        self.env['sanad.doctor'].create({
            'partner_id': self.partner_1.id, 'license_number': 'LIC-A',
        })
        with self.assertRaises(Exception), mute_logger('odoo.sql_db'):
            self.env['sanad.doctor'].create({
                'partner_id': self.partner_1.id, 'license_number': 'LIC-B',
            })

    def test_same_user_cannot_be_linked_to_two_doctors(self):
        self.env['sanad.doctor'].create({
            'partner_id': self.partner_1.id, 'user_id': self.user_1.id,
            'license_number': 'LIC-C',
        })
        with self.assertRaises(ValidationError):
            self.env['sanad.doctor'].create({
                'partner_id': self.partner_2.id, 'user_id': self.user_1.id,
                'license_number': 'LIC-D',
            })
