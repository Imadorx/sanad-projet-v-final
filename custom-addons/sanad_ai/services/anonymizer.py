# -*- coding: utf-8 -*-
"""PHI anonymization/redaction layer.

Hard requirement (PRD 15 / architecture decision): patient identifiers
MUST be stripped or masked before any data leaves the platform for an
external AI provider. This module is the single choke point that every
AI-facing code path in sanad_ai routes through - nothing calls an
external provider without going through anonymize_text() first.

Two complementary techniques are used:
1. Known-value substitution: identifiers we already know from the ORM
   (patient name, doctor name, phone, email, address, license/patient
   IDs) are replaced with stable placeholder tokens BEFORE any text is
   built into a prompt.
2. Pattern-based redaction: a regex safety net catches identifiers that
   may appear in free-text fields (consultation notes, lab report text)
   that weren't explicitly enumerated - emails, phone numbers, dates of
   birth, and ID-number-like sequences.

This is a defense-in-depth pair, not a single point of failure: even if
a caller forgets to pass a known identifier into replacements, the
pattern layer still catches common PHI shapes.
"""
import re

EMAIL_RE = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
PHONE_RE = re.compile(r'(\+?\d[\d\s\-().]{7,}\d)')
DATE_RE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b')
ID_LIKE_RE = re.compile(r'\b[A-Z]{1,4}-?\d{4,}\b')  # e.g. license numbers, MRNs


def build_replacement_map(patient=None, doctor=None, extra=None):
    """Build a dict of known-identifier -> placeholder pairs from ORM
    records. Longer/more specific strings are ordered first by the
    caller (anonymize_text) so partial-name collisions don't leave
    fragments unredacted (e.g. redact full name before first name)."""
    mapping = {}
    if patient:
        if patient.name:
            mapping[patient.name] = '[PATIENT_NAME]'
        if patient.phone:
            mapping[patient.phone] = '[PATIENT_PHONE]'
        if patient.email:
            mapping[patient.email] = '[PATIENT_EMAIL]'
        if patient.address:
            mapping[patient.address] = '[PATIENT_ADDRESS]'
        if patient.emergency_contact_name:
            mapping[patient.emergency_contact_name] = '[EMERGENCY_CONTACT]'
        if patient.emergency_contact_phone:
            mapping[patient.emergency_contact_phone] = '[EMERGENCY_CONTACT_PHONE]'
    if doctor:
        if doctor.name:
            mapping[doctor.name] = '[DOCTOR_NAME]'
        if doctor.phone:
            mapping[doctor.phone] = '[DOCTOR_PHONE]'
        if doctor.email:
            mapping[doctor.email] = '[DOCTOR_EMAIL]'
        if doctor.license_number:
            mapping[doctor.license_number] = '[LICENSE_NUMBER]'
    if extra:
        mapping.update(extra)
    return mapping


def anonymize_text(text, replacement_map=None):
    """Redact known identifiers (by exact substring match, longest
    first) then sweep with pattern-based regexes for anything left.
    Returns (anonymized_text, applied: bool)."""
    if not text:
        return text, False

    applied = False
    result = text

    if replacement_map:
        # Longest strings first so "Dr. Amina El Fassi" is replaced
        # before a bare "Amina" fragment could partially match elsewhere.
        for original in sorted(replacement_map.keys(), key=len, reverse=True):
            if not original:
                continue
            if original in result:
                result = result.replace(original, replacement_map[original])
                applied = True

    for pattern, placeholder in (
        (EMAIL_RE, '[EMAIL]'),
        (DATE_RE, '[DATE]'),
        (PHONE_RE, '[PHONE]'),
        (ID_LIKE_RE, '[ID]'),
    ):
        new_result, count = pattern.subn(placeholder, result)
        if count:
            applied = True
        result = new_result

    return result, applied


def anonymize_patient_summary(patient):
    """Build an anonymized structured summary of a patient suitable for
    inclusion in an AI prompt - demographic categories only, never name/
    contact/address. Used by explain()/search() when patient context is
    needed for a medically-relevant explanation (e.g. age-appropriate
    dosing context) without ever sending identity."""
    return {
        'age': patient.age,
        'gender': patient.gender,
        'blood_group': patient.blood_group,
        'allergies': patient.allergies or 'none recorded',
        'chronic_diseases': patient.chronic_diseases or 'none recorded',
    }
