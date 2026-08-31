#!/usr/bin/env python3
"""
SANAD Demo Data Validator
=========================
Validates that the demo dataset is complete and correct.
Run after create_demo_data.py to verify everything is in place.

Usage (inside Odoo shell):
    exec(open('/mnt/extra-addons/scripts/validate_demo_data.py').read())
"""

from odoo import api


def validate(env):
    """Run all validation checks. Returns (passed: bool, report: list[str])."""
    report = []
    errors = []
    warnings = []

    def ok(msg):
        report.append(f'  OK: {msg}')

    def warn(msg):
        report.append(f'  WARN: {msg}')
        warnings.append(msg)

    def fail(msg):
        report.append(f'  FAIL: {msg}')
        errors.append(msg)

    # ---- 1. Models exist in registry ----
    report.append('')
    report.append('1. MODEL REGISTRY CHECK')
    report.append('-' * 40)
    required_models = [
        'sanad.doctor', 'sanad.patient', 'sanad.patient.doctor.rel',
        'sanad.medical.cabinet', 'sanad.laboratory.org', 'sanad.pharmacy.org',
        'sanad.medical.specialty', 'sanad.consultation', 'sanad.prescription',
        'sanad.medical.record', 'sanad.lab.request', 'sanad.lab.result',
        'sanad.chat.conversation', 'sanad.ai.log',
    ]
    for model_name in required_models:
        try:
            model = env['ir.model'].search([('model', '=', model_name)], limit=1)
            if model:
                ok(f'Model {model_name} registered')
            else:
                fail(f'Model {model_name} NOT found in registry')
        except Exception:
            fail(f'Model {model_name} NOT accessible')

    # ---- 2. Security groups ----
    report.append('')
    report.append('2. SECURITY GROUPS CHECK')
    report.append('-' * 40)
    groups = [
        'sanad_core.group_sanad_admin',
        'sanad_core.group_sanad_doctor',
        'sanad_core.group_sanad_patient',
        'sanad_core.group_sanad_laboratory',
        'sanad_core.group_sanad_pharmacy',
    ]
    for xml_id in groups:
        try:
            g = env.ref(xml_id)
            ok(f'Group {xml_id} exists (id={g.id})')
        except Exception:
            fail(f'Group {xml_id} NOT found')

    # ---- 3. Users and roles ----
    report.append('')
    report.append('3. USERS AND ROLES CHECK')
    report.append('-' * 40)
    user_checks = [
        ('doctor.ahmed@sanad.local', 'group_sanad_doctor', 'Dr. Ahmed Benali'),
        ('doctor.sara@sanad.local', 'group_sanad_doctor', 'Dr. Sara Amrani'),
        ('doctor.youssef@sanad.local', 'group_sanad_doctor', 'Dr. Youssef Alaoui'),
        ('patient.mohamed@sanad.local', 'group_sanad_patient', 'Mohamed Amine'),
        ('patient.sara.el@sanad.local', 'group_sanad_patient', 'Sara El Idrissi'),
        ('patient.yassine@sanad.local', 'group_sanad_patient', 'Yassine Bennani'),
        ('lab.sanad@sanad.local', 'group_sanad_laboratory', 'SANAD Lab Technician'),
        ('lab.alamal@sanad.local', 'group_sanad_laboratory', 'Al Amal Lab Technician'),
        ('pharmacy.sanad@sanad.local', 'group_sanad_pharmacy', 'SANAD Pharmacist'),
        ('pharmacy.alamal@sanad.local', 'group_sanad_pharmacy', 'Al Amal Pharmacist'),
    ]
    for login, expected_group, expected_name in user_checks:
        user = env['res.users'].search([('login', '=', login)], limit=1)
        if not user:
            fail(f'User {login} not found')
            continue
        if user.has_group(f'sanad_core.{expected_group}'):
            ok(f'User {login} ({user.name}) has group {expected_group}')
        else:
            fail(f'User {login} missing expected group {expected_group}')

    # ---- 4. Doctors ----
    report.append('')
    report.append('4. DOCTORS CHECK')
    report.append('-' * 40)
    Doctor = env['sanad.doctor']
    doctor_emails = [
        'doctor.ahmed@sanad.local',
        'doctor.sara@sanad.local',
        'doctor.youssef@sanad.local',
    ]
    for email in doctor_emails:
        user = env['res.users'].search([('login', '=', email)], limit=1)
        if user:
            doctor = Doctor.search([('user_id', '=', user.id)], limit=1)
            if doctor:
                ok(f'Doctor: {doctor.name}, Specialty: {doctor.specialty_id.name}, '
                    f'Cabinet: {doctor.cabinet_id.name}, License: {doctor.license_number}')
            else:
                fail(f'No doctor profile for user {email}')
        else:
            fail(f'User {email} not found')

    # ---- 5. Patients ----
    report.append('')
    report.append('5. PATIENTS CHECK')
    report.append('-' * 40)
    Patient = env['sanad.patient']
    patient_emails = [
        'patient.mohamed@sanad.local',
        'patient.sara.el@sanad.local',
        'patient.yassine@sanad.local',
    ]
    for email in patient_emails:
        user = env['res.users'].search([('login', '=', email)], limit=1)
        if user:
            patient = Patient.search([('user_id', '=', user.id)], limit=1)
            if patient:
                ok(f'Patient: {patient.name}, Age: {patient.age}, Gender: {patient.gender}, '
                    f'Blood: {patient.blood_group}')
            else:
                fail(f'No patient profile for user {email}')
        else:
            fail(f'User {email} not found')

    # ---- 6. Care Relationships ----
    report.append('')
    report.append('6. CARE RELATIONSHIPS CHECK')
    report.append('-' * 40)
    CareRel = env['sanad.patient.doctor.rel']
    rel_checks = [
        ('patient.mohamed@sanad.local', 'doctor.ahmed@sanad.local', 'primary'),
        ('patient.sara.el@sanad.local', 'doctor.ahmed@sanad.local', 'consulting'),
        ('patient.sara.el@sanad.local', 'doctor.sara@sanad.local', 'primary'),
        ('patient.yassine@sanad.local', 'doctor.youssef@sanad.local', 'primary'),
    ]
    for pat_email, doc_email, expected_type in rel_checks:
        pat_user = env['res.users'].search([('login', '=', pat_email)], limit=1)
        doc_user = env['res.users'].search([('login', '=', doc_email)], limit=1)
        if pat_user and doc_user:
            patient = Patient.search([('user_id', '=', pat_user.id)], limit=1)
            doctor = Doctor.search([('user_id', '=', doc_user.id)], limit=1)
            if patient and doctor:
                rel = CareRel.search([
                    ('patient_id', '=', patient.id),
                    ('doctor_id', '=', doctor.id),
                    ('active', '=', True),
                ], limit=1)
                if rel:
                    ok(f'Active care rel: {patient.name} <-> {doctor.name} [{rel.relationship_type}]')
                else:
                    fail(f'Missing active care rel: {patient.name} <-> {doctor.name}')
            else:
                fail(f'Could not find patient/doctor for relationship check')
        else:
            fail(f'Could not find users for relationship check')

    # ---- 7. Consultations ----
    report.append('')
    report.append('7. CONSULTATIONS CHECK')
    report.append('-' * 40)
    Consultation = env['sanad.consultation']
    consultations = Consultation.search([])
    ok(f'Total consultations: {len(consultations)}')
    for c in consultations:
        ok(f'  - {c.patient_id.name}: {c.reason} (Dr. {c.doctor_id.name}, {c.date.date()})')

    # ---- 8. Medical Records ----
    report.append('')
    report.append('8. MEDICAL RECORDS CHECK')
    report.append('-' * 40)
    MedicalRecord = env['sanad.medical.record']
    records = MedicalRecord.search([])
    ok(f'Total medical records: {len(records)}')
    for r in records:
        ok(f'  - Patient: {r.patient_id.name}, Consultations: {r.consultation_count}, '
            f'Prescriptions: {r.prescription_count}')

    # ---- 9. Lab Requests and Results ----
    report.append('')
    report.append('9. LABORATORY CHECK')
    report.append('-' * 40)
    LabRequest = env['sanad.lab.request']
    LabResult = env['sanad.lab.result']
    lab_reqs = LabRequest.search([])
    lab_results = LabResult.search([])
    ok(f'Total lab requests: {len(lab_reqs)}')
    for lr in lab_reqs:
        ok(f'  - {lr.patient_id.name}: {lr.analysis_type} [{lr.status}] -> {lr.laboratory_id.name}')
    ok(f'Total lab results: {len(lab_results)}')
    for lr in lab_results:
        ok(f'  - {lr.analysis_name}: {lr.result_value} {lr.unit} (range: {lr.reference_range})')

    # ---- 10. Prescriptions ----
    report.append('')
    report.append('10. PRESCRIPTIONS CHECK')
    report.append('-' * 40)
    Prescription = env['sanad.prescription']
    prescriptions = Prescription.search([])
    ok(f'Total prescriptions: {len(prescriptions)}')
    for p in prescriptions:
        ok(f'  - {p.patient_id.name}: {p.medication} [{p.pharmacy_status}] '
            f'-> {p.pharmacy_id.name if p.pharmacy_id else "No pharmacy"}')

    # ---- 11. Pharmacy workflow states ----
    report.append('')
    report.append('11. PHARMACY WORKFLOW CHECK')
    report.append('-' * 40)
    for status in ['pending', 'received', 'prepared', 'completed']:
        count = Prescription.search([('pharmacy_status', '=', status)]).count()
        ok(f'  Prescriptions with status "{status}": {count}')

    # ---- 12. Lab workflow states ----
    report.append('')
    report.append('12. LAB WORKFLOW CHECK')
    report.append('-' * 40)
    for status in ['draft', 'sent', 'accepted', 'processing', 'completed', 'cancelled']:
        count = LabRequest.search([('status', '=', status)]).count()
        ok(f'  Lab requests with status "{status}": {count}')

    # ---- 13. Chat Conversations ----
    report.append('')
    report.append('13. CHAT CONVERSATIONS CHECK')
    report.append('-' * 40)
    ChatConversation = env['sanad.chat.conversation']
    conversations = ChatConversation.search([])
    ok(f'Total conversations: {len(conversations)}')
    for conv in conversations:
        ok(f'  - Type: {conv.conversation_type}, Participants: {conv.display_name}')

    # ---- 14. Organizations ----
    report.append('')
    report.append('14. ORGANIZATIONS CHECK')
    report.append('-' * 40)
    cabinets = env['sanad.medical.cabinet'].search([])
    labs = env['sanad.laboratory.org'].search([])
    pharmacies = env['sanad.pharmacy.org'].search([])
    ok(f'Medical cabinets: {len(cabinets)}')
    for c in cabinets:
        ok(f'  - {c.name}')
    ok(f'Laboratories: {len(labs)}')
    for l in labs:
        staff_count = len(l.user_ids)
        ok(f'  - {l.name} ({staff_count} staff)')
    ok(f'Pharmacies: {len(pharmacies)}')
    for p in pharmacies:
        staff_count = len(p.user_ids)
        ok(f'  - {p.name} ({staff_count} staff)')

    # ---- 15. KPI Evolution Check ----
    report.append('')
    report.append('15. KPI EVOLUTION CHECK')
    report.append('-' * 40)
    # Check Mohamed's Hemoglobin results
    mohamed_patient = Patient.search([('partner_id.email', '=', 'patient.mohamed@sanad.local')], limit=1)
    if mohamed_patient:
        kpi = LabResult.get_kpi_evolution(mohamed_patient.id, 'Hemoglobin')
        ok(f'KPI evolution for Mohamed/Hemoglobin: {len(kpi)} data points')
        for k in kpi:
            ok(f'  - {k["date"].date()}: {k["value"]} {k["unit"]}')

    # ---- 16. Frontend Route Validation ----
    report.append('')
    report.append('16. FRONTEND ROUTE VALIDATION')
    report.append('-' * 40)
    frontend_routes = {
        '/patient': 'patient.mohamed@sanad.local',
        '/doctor': 'doctor.ahmed@sanad.local',
        '/laboratory': 'lab.sanad@sanad.local',
        '/pharmacy': 'pharmacy.sanad@sanad.local',
        '/admin': 'admin@sanad.local',
    }
    for route, login in frontend_routes.items():
        user = env['res.users'].search([('login', '=', login)], limit=1)
        if user:
            ok(f'Route {route}: User {login} exists')
        else:
            warn(f'Route {route}: User {login} not found (may use admin)')

    # ---- Summary ----
    report.append('')
    report.append('=' * 60)
    report.append('VALIDATION SUMMARY')
    report.append('=' * 60)
    report.append(f'  Total checks: {len(report) - 1}')
    report.append(f'  Errors: {len(errors)}')
    report.append(f'  Warnings: {len(warnings)}')
    if errors:
        report.append('')
        report.append('ERRORS:')
        for e in errors:
            report.append(f'  {e}')
    if warnings:
        report.append('')
        report.append('WARNINGS:')
        for w in warnings:
            report.append(f'  {w}')
    report.append('')
    report.append('RESULT: ' + ('PASSED' if not errors else 'FAILED'))

    return len(errors) == 0, report


if __name__ == '__main__':
    print('This script must be run inside an Odoo shell environment.')
    print('Usage:')
    print('  docker exec -it sanad_odoo odoo shell -d sanad_db -c /etc/odoo/odoo.conf')
    print('  >>> exec(open("/mnt/extra-addons/scripts/validate_demo_data.py").read())')
