# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged
from odoo.addons.sanad_ai.services.safety_filter import (
    check_response_safety, finalize_response,
)


@tagged('post_install', '-at_install', 'sanad_ai')
class TestSafetyFilter(TransactionCase):
    """AI output safety enforcement tests (Phase 8) - the hard PRD
    constraint 'AI must NEVER diagnose/prescribe' as an executable test,
    not just a system-prompt instruction."""

    def test_diagnostic_language_is_blocked(self):
        unsafe = 'Based on your results, you have diabetes and need treatment.'
        is_safe, pattern = check_response_safety(unsafe)
        self.assertFalse(is_safe)
        self.assertIsNotNone(pattern)

    def test_prescriptive_dosage_language_is_blocked(self):
        unsafe = 'I recommend you take 500mg of metformin twice daily.'
        is_safe, _ = check_response_safety(unsafe)
        self.assertFalse(is_safe)

    def test_direct_instruction_to_take_medication_is_blocked(self):
        unsafe = 'You should take this medication right away.'
        is_safe, _ = check_response_safety(unsafe)
        self.assertFalse(is_safe)

    def test_dismissing_need_for_doctor_is_blocked(self):
        unsafe = 'You do not need to see a doctor for this.'
        is_safe, _ = check_response_safety(unsafe)
        self.assertFalse(is_safe)

    def test_educational_explanation_is_allowed(self):
        safe = 'A complete blood count measures red cells, white cells, and platelets.'
        is_safe, pattern = check_response_safety(safe)
        self.assertTrue(is_safe)
        self.assertIsNone(pattern)

    def test_factual_medication_description_is_allowed(self):
        """Describing what a medication is generally used for (factual,
        not directive) should not be blocked - the filter targets
        directive/diagnostic language, not all mentions of medicine."""
        safe = 'Metformin is commonly used to help manage blood sugar levels.'
        is_safe, _ = check_response_safety(safe)
        self.assertTrue(is_safe)

    def test_disclaimer_always_appended(self):
        text = 'A CBC test checks blood cell counts.'
        finalized = finalize_response(text)
        self.assertIn('educational', finalized.lower())
        self.assertIn('consult', finalized.lower())

    def test_disclaimer_not_duplicated(self):
        text = 'Some explanation.'
        once = finalize_response(text)
        twice = finalize_response(once)
        self.assertEqual(once.count('educational only'), twice.count('educational only'))
