#!/usr/bin/env python3
"""
SANAD Demo Data Creator
=======================
Creates a complete, logically connected, realistic demo dataset for the
SANAD Healthcare Platform. Designed to be idempotent - running it twice
will NOT create duplicates.

Usage (inside Odoo container):
    docker exec -it sanad_odoo odoo shell -d sanad_db -c /etc/odoo/odoo.conf
    >>> exec(open('/mnt/extra-addons/scripts/create_demo_data.py').read())

Or via odoo-bin:
    odoo shell -d sanad_db --addons-path=/mnt/extra-addons
    >>> exec(open('scripts/create_demo_data.py').read())

IMPORTANT: This script uses demo XML IDs where they exist. New records
use deterministic emails/names for idempotency.
"""

import sys
from datetime import date, datetime, timedelta
from odoo import api, SUPERUSER_ID

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ADMIN_EMAIL = 'admin@sanad.local'

# Demo emails - deterministic for idempotency
DOCTOR_EMAILS = {
    'ahmed': 'doctor.ahmed@sanad.local',
    'sara': 'doctor.sara@sanad.local',
    'youssef': 'doctor.youssef@sanad.local',
}

PATIENT_EMAILS = {
    'mohamed': 'patient.mohamed@sanad.local',
    'sara_el': 'patient.sara.el@sanad.local',
    'yassine': 'patient.yassine@sanad.local',
}

LAB_EMAILS = {
    'sanad_lab': 'lab.sanad@sanad.local',
    'al_amal': 'lab.alamal@sanad.local',
}

PHARMACY_EMAILS = {
    'sanad_pharm': 'pharmacy.sanad@sanad.local',
    'al_amal': 'pharmacy.alamal@sanad.local',
}


def log(msg):
    print(f'[SANAD DEMO] {msg}')


def run(env):
    """Main entry point. Call with an Odoo environment."""
    Partner = env['res.partner']
    User = env['res.users']
    Doctor = env['sanad.doctor']
    Patient = env['sanad.patient']
    CareRel = env['sanad.patient.doctor.rel']
    Specialty = env['sanad.medical.specialty']
    Cabinet = env['sanad.medical.cabinet']
    LabOrg = env['sanad.laboratory.org']
    PharmacyOrg = env['sanad.pharmacy.org']
    Consultation = env['sanad.consultation']
    Prescription = env['sanad.prescription']
    LabRequest = env['sanad.lab.request']
    LabResult = env['sanad.lab.result']
    MedicalRecord = env['sanad.medical.record']
    ChatConversation = env['sanad.chat.conversation']
    AiLog = env['sanad.ai.log']

    # Get security groups
    group_admin = env.ref('sanad_core.group_sanad_admin')
    group_doctor = env.ref('sanad_core.group_sanad_doctor')
    group_patient = env.ref('sanad_core.group_sanad_patient')
    group_lab = env.ref('sanad_core.group_sanad_laboratory')
    group_pharmacy = env.ref('sanad_core.group_sanad_pharmacy')

    # Get demo XML ID references (existing data)
    specialty_general = env.ref('sanad_core.demo_specialty_general')
    specialty_cardio = env.ref('sanad_core.demo_specialty_cardio')
    specialty_pedia = env.ref('sanad_core.demo_specialty_pedia')
    cabinet_main = env.ref('sanad_core.demo_cabinet_main')
    lab_main = env.ref('sanad_core.demo_lab_main')
    pharmacy_main = env.ref('sanad_core.demo_pharmacy_main')
    existing_doctor_1 = env.ref('sanad_core.demo_doctor_1')  # Dr. Amina El Fassi
    existing_patient_1 = env.ref('sanad_patient.demo_patient_1')  # Youssef Bennani

    # =========================================================================
    # STEP 1: Create Organizations (reuse existing + add new)
    # =========================================================================
    log('Step 1: Creating organizations...')

    # Existing: SANAD Central Lab, SANAD Central Pharmacy, SANAD Central Cabinet
    # New: SANAD LAB, Laboratoire Al Amal, Pharmacie SANAD, Pharmacie Al Amal

    lab_sanad = LabOrg.search([('name', '=', 'SANAD LAB')], limit=1)
    if not lab_sanad:
        lab_sanad = LabOrg.create({
            'name': 'SANAD LAB',
            'phone': '+212 5 00 00 00 10',
            'email': 'contact@sanadlab.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created SANAD LAB')
    else:
        log('  Reusing SANAD LAB')

    lab_al_amal = LabOrg.search([('name', '=', 'Laboratoire Al Amal')], limit=1)
    if not lab_al_amal:
        lab_al_amal = LabOrg.create({
            'name': 'Laboratoire Al Amal',
            'phone': '+212 5 00 00 00 11',
            'email': 'contact@alamal-lab.example.com',
            'address': 'Rabat, Morocco',
        })
        log('  Created Laboratoire Al Amal')
    else:
        log('  Reusing Laboratoire Al Amal')

    pharm_sanad = PharmacyOrg.search([('name', '=', 'Pharmacie SANAD')], limit=1)
    if not pharm_sanad:
        pharm_sanad = PharmacyOrg.create({
            'name': 'Pharmacie SANAD',
            'phone': '+212 5 00 00 00 12',
            'email': 'contact@pharmaciesanad.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created Pharmacie SANAD')
    else:
        log('  Reusing Pharmacie SANAD')

    pharm_al_amal = PharmacyOrg.search([('name', '=', 'Pharmacie Al Amal')], limit=1)
    if not pharm_al_amal:
        pharm_al_amal = PharmacyOrg.create({
            'name': 'Pharmacie Al Amal',
            'phone': '+212 5 00 00 00 13',
            'email': 'contact@pharmaciealamal.example.com',
            'address': 'Rabat, Morocco',
        })
        log('  Created Pharmacie Al Amal')
    else:
        log('  Reusing Pharmacie Al Amal')

    cabinet_main = Cabinet.search([('name', '=', 'Cabinet Médical SANAD')], limit=1)
    if not cabinet_main:
        cabinet_main = Cabinet.create({
            'name': 'Cabinet Médical SANAD',
            'phone': '+212 5 00 00 00 20',
            'email': 'contact@cabinet-sanad.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created Cabinet Médical SANAD')
    else:
        log('  Reusing Cabinet Médical SANAD')

    # =========================================================================
    # STEP 2: Create Doctors
    # =========================================================================
    log('Step 2: Creating doctors...')

    def create_doctor(name, email, phone, specialty, license_num, cabinet, professional_info=''):
        """Create a doctor with partner + user + doctor profile."""
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({
                'name': name,
                'email': email,
                'phone': phone,
                'company_type': 'person',
            })
            log(f'    Created partner: {name}')
        else:
            log(f'    Reusing partner: {name}')

        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name,
                'login': email,
                'partner_id': partner.id,
                'groups_id': [(4, group_doctor.id)],
            })
            log(f'    Created user: {email}')
        else:
            log(f'    Reusing user: {email}')

        doctor = Doctor.search([('partner_id', '=', partner.id)], limit=1)
        if not doctor:
            doctor = Doctor.create({
                'partner_id': partner.id,
                'user_id': user.id,
                'specialty_id': specialty.id,
                'license_number': license_num,
                'cabinet_id': cabinet.id,
                'professional_info': professional_info,
            })
            log(f'    Created doctor: {name}')
        else:
            log(f'    Reusing doctor: {name}')

        return doctor

    dr_ahmed = create_doctor(
        name='Dr. Ahmed Benali',
        email=DOCTOR_EMAILS['ahmed'],
        phone='+212 6 00 00 00 01',
        specialty=specialty_general,
        license_num='SANAD-LIC-001',
        cabinet=cabinet_main,
        professional_info='General practitioner with 10 years of experience. '
                          'Specializes in preventive medicine and chronic disease management.',
    )

    dr_sara = create_doctor(
        name='Dr. Sara Amrani',
        email=DOCTOR_EMAILS['sara'],
        phone='+212 6 00 00 00 02',
        specialty=specialty_cardio,
        license_num='SANAD-LIC-002',
        cabinet=cabinet_main,
        professional_info='Cardiologist with 12 years of experience. '
                          'Specializes in interventional cardiology and heart failure management.',
    )

    dr_youssef = create_doctor(
        name='Dr. Youssef Alaoui',
        email=DOCTOR_EMAILS['youssef'],
        phone='+212 6 00 00 00 03',
        specialty=specialty_pedia,
        license_num='SANAD-LIC-003',
        cabinet=cabinet_main,
        professional_info='Pediatrician with 8 years of experience. '
                          'Specializes in childhood vaccinations and developmental pediatrics.',
    )

    # =========================================================================
    # STEP 3: Create Lab/Pharmacy Staff Users
    # =========================================================================
    log('Step 3: Creating lab and pharmacy staff users...')

    def create_staff_user(name, email, phone, group, org, org_field='user_ids'):
        """Create a staff user and link to their organization."""
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({
                'name': name,
                'email': email,
                'phone': phone,
                'company_type': 'person',
            })
            log(f'    Created staff partner: {name}')
        else:
            log(f'    Reusing staff partner: {name}')

        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name,
                'login': email,
                'partner_id': partner.id,
                'groups_id': [(4, group.id)],
            })
            log(f'    Created staff user: {email}')
        else:
            log(f'    Reusing staff user: {email}')

        # Link user to org if not already linked
        if org and user.id not in org.user_ids.ids:
            org.write({org_field: [(4, user.id)]})
            log(f'    Linked {name} to {org.name}')

        return user

    lab_user_sanad = create_staff_user(
        name='SANAD Lab Technician',
        email=LAB_EMAILS['sanad_lab'],
        phone='+212 6 00 00 00 20',
        group=group_lab,
        org=lab_sanad,
    )

    lab_user_al_amal = create_staff_user(
        name='Al Amal Lab Technician',
        email=LAB_EMAILS['al_amal'],
        phone='+212 6 00 00 00 21',
        group=group_lab,
        org=lab_al_amal,
    )

    pharm_user_sanad = create_staff_user(
        name='SANAD Pharmacist',
        email=PHARMACY_EMAILS['sanad_pharm'],
        phone='+212 6 00 00 00 30',
        group=group_pharmacy,
        org=pharm_sanad,
    )

    pharm_user_al_amal = create_staff_user(
        name='Al Amal Pharmacist',
        email=PHARMACY_EMAILS['al_amal'],
        phone='+212 6 00 00 00 31',
        group=group_pharmacy,
        org=pharm_al_amal,
    )

    # =========================================================================
    # STEP 4: Create Patients
    # =========================================================================
    log('Step 4: Creating patients...')

    def create_patient(name, email, phone, birth_date, gender, blood_group,
                       allergies='', chronic_diseases='', emergency_name='',
                       emergency_phone='', emergency_relation=''):
        """Create a patient with partner + user + patient profile."""
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({
                'name': name,
                'email': email,
                'phone': phone,
                'company_type': 'person',
            })
            log(f'    Created patient partner: {name}')
        else:
            log(f'    Reusing patient partner: {name}')

        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name,
                'login': email,
                'partner_id': partner.id,
                'groups_id': [(4, group_patient.id)],
            })
            log(f'    Created patient user: {email}')
        else:
            log(f'    Reusing patient user: {email}')

        patient = Patient.search([('partner_id', '=', partner.id)], limit=1)
        if not patient:
            patient = Patient.create({
                'partner_id': partner.id,
                'user_id': user.id,
                'birth_date': birth_date,
                'gender': gender,
                'blood_group': blood_group,
                'allergies': allergies,
                'chronic_diseases': chronic_diseases,
                'emergency_contact_name': emergency_name,
                'emergency_contact_phone': emergency_phone,
                'emergency_contact_relation': emergency_relation,
            })
            log(f'    Created patient: {name}')
        else:
            log(f'    Reusing patient: {name}')

        return patient

    patient_mohamed = create_patient(
        name='Mohamed Amine',
        email=PATIENT_EMAILS['mohamed'],
        phone='+212 6 10 20 30 40',
        birth_date=date(1990, 5, 15),
        gender='male',
        blood_group='a_pos',
        allergies='Aspirin',
        chronic_diseases='Hypertension',
        emergency_name='Fatima Amine',
        emergency_phone='+212 6 99 88 77 66',
        emergency_relation='Wife',
    )

    patient_sara = create_patient(
        name='Sara El Idrissi',
        email=PATIENT_EMAILS['sara_el'],
        phone='+212 6 20 30 40 50',
        birth_date=date(1985, 8, 22),
        gender='female',
        blood_group='b_pos',
        allergies='None',
        chronic_diseases='Type 2 Diabetes',
        emergency_name='Omar El Idrissi',
        emergency_phone='+212 6 77 88 99 00',
        emergency_relation='Husband',
    )

    patient_yassine = create_patient(
        name='Yassine Bennani',
        email=PATIENT_EMAILS['yassine'],
        phone='+212 6 30 40 50 60',
        birth_date=date(2015, 3, 10),
        gender='male',
        blood_group='o_pos',
        allergies='Peanuts',
        chronic_diseases='None',
        emergency_name='Leila Bennani',
        emergency_phone='+212 6 66 55 44 33',
        emergency_relation='Mother',
    )

    # =========================================================================
    # STEP 5: Create Care Relationships
    # =========================================================================
    log('Step 5: Creating care relationships...')

    def create_care_rel(patient, doctor, rel_type='primary', notes=''):
        """Create a care relationship if it doesn't exist."""
        existing = CareRel.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('relationship_type', '=', rel_type),
        ], limit=1)
        if existing:
            log(f'    Reusing care rel: {patient.name} <-> {doctor.name} ({rel_type})')
            return existing
        rel = CareRel.create({
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'relationship_type': rel_type,
            'start_date': date(2026, 1, 1),
            'notes': notes,
        })
        log(f'    Created care rel: {patient.name} <-> {doctor.name} ({rel_type})')
        return rel

    # Dr. Ahmed -> Mohamed Amine (primary)
    create_care_rel(patient_mohamed, dr_ahmed, 'primary',
                    'Primary care physician - manages hypertension')

    # Dr. Ahmed -> Sara El Idrissi (consulting)
    create_care_rel(patient_sara, dr_ahmed, 'consulting',
                    'General consultation for diabetes management')

    # Dr. Sara Amrani -> Sara El Idrissi (primary)
    create_care_rel(patient_sara, dr_sara, 'primary',
                    'Cardiology - cardiac evaluation for diabetic patient')

    # Dr. Youssef Alaoui -> Yassine Bennani (primary)
    create_care_rel(patient_yassine, dr_youssef, 'primary',
                    'Pediatric care - regular checkups')

    # =========================================================================
    # STEP 6: Create Consultations (connected to care relationships)
    # =========================================================================
    log('Step 6: Creating consultations...')

    def create_consultation(patient, doctor, reason, symptoms='', observations='',
                            report='', offset_days=0):
        """Create a consultation with proper date offset."""
        existing = Consultation.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('reason', '=', reason),
        ], limit=1)
        if existing:
            log(f'    Reusing consultation: {reason} for {patient.name}')
            return existing
        consultation = Consultation.sudo().create({
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'reason': reason,
            'symptoms': symptoms,
            'observations': observations,
            'report': report,
            'date': datetime.now() - timedelta(days=offset_days),
        })
        log(f'    Created consultation: {reason} for {patient.name}')
        return consultation

    # Mohamed Amine - Initial consultation with Dr. Ahmed
    consult_1 = create_consultation(
        patient=patient_mohamed,
        doctor=dr_ahmed,
        reason='Initial hypertension evaluation',
        symptoms='Headaches, occasional dizziness, fatigue',
        observations='Blood pressure elevated at 150/95. Patient reports '
                     'stress at work and poor sleep habits. No family history '
                     'of cardiovascular disease.',
        report='<p>Preliminary diagnosis: Stage 1 Hypertension. '
               'Recommend lifestyle modifications and follow-up in 2 weeks.</p>',
        offset_days=21,
    )

    # Mohamed Amine - Follow-up
    consult_2 = create_consultation(
        patient=patient_mohamed,
        doctor=dr_ahmed,
        reason='Hypertension follow-up',
        symptoms='Reduced headaches, occasional dizziness',
        observations='Blood pressure improved at 138/88. Patient has started '
                     'walking 30 minutes daily. Medication compliance confirmed.',
        report='<p>Progress positive. Continue current management. '
               'Order blood work for lipid panel and kidney function.</p>',
        offset_days=7,
    )

    # Sara El Idrissi - Consultation with Dr. Ahmed
    consult_3 = create_consultation(
        patient=patient_sara,
        doctor=dr_ahmed,
        reason='Diabetes management review',
        symptoms='Increased thirst, frequent urination',
        observations='HbA1c at 8.2%. Current medication Metformin 500mg. '
                     'Referred to cardiology for cardiac evaluation due to '
                     'diabetes duration.',
        report='<p>Type 2 Diabetes - suboptimal control. Medication adjustment '
               'recommended. Cardiology referral for baseline cardiac assessment.</p>',
        offset_days=14,
    )

    # Sara El Idrissi - Consultation with Dr. Sara (cardiology)
    consult_4 = create_consultation(
        patient=patient_sara,
        doctor=dr_sara,
        reason='Cardiac evaluation for diabetes',
        symptoms='None cardiac-specific',
        observations='ECG normal. Echocardiogram shows normal left ventricular '
                     'function. No signs of diabetic cardiomyopathy.',
        report='<p>Cardiac evaluation complete. No evidence of cardiac '
               'complications from diabetes. Continue diabetes management '
               'with primary physician.</p>',
        offset_days=10,
    )

    # Yassine Bennani - Checkup with Dr. Youssef
    consult_5 = create_consultation(
        patient=patient_yassine,
        doctor=dr_youssef,
        reason='Annual pediatric checkup',
        symptoms='None - routine visit',
        observations='Growth parameters within normal limits. BMI normal. '
                     'Vaccination schedule up to date. No concerns reported by mother.',
        report='<p>Annual checkup normal. All developmental milestones met. '
               'Continue regular follow-up.</p>',
        offset_days=5,
    )

    # =========================================================================
    # STEP 7: Create Lab Requests and Results
    # =========================================================================
    log('Step 7: Creating lab requests and results...')

    # --- Lab Request 1: Mohamed Amine - Blood Work ---
    lab_req_1 = LabRequest.search([
        ('patient_id', '=', patient_mohamed.id),
        ('analysis_type', '=', 'Complete Blood Count'),
    ], limit=1)
    if not lab_req_1:
        lab_req_1 = LabRequest.sudo().create({
            'patient_id': patient_mohamed.id,
            'doctor_id': dr_ahmed.id,
            'laboratory_id': lab_sanad.id,
            'consultation_id': consult_2.id,
            'analysis_type': 'Complete Blood Count',
            'instructions': 'Fasting required. Patient on hypertension medication.',
        })
        log('    Created lab request: CBC for Mohamed Amine')
    else:
        log('    Reusing lab request: CBC for Mohamed Amine')

    # Process through workflow
    if lab_req_1.status == 'draft':
        lab_req_1.sudo().action_send()
        log('    Sent lab request')
    if lab_req_1.status == 'sent':
        lab_req_1.sudo().action_accept()
        log('    Accepted lab request')
    if lab_req_1.status == 'accepted':
        lab_req_1.sudo().action_start_processing()
        log('    Started processing')

    # Add results if none exist
    if not lab_req_1.result_ids:
        LabResult.sudo().create({
            'request_id': lab_req_1.id,
            'analysis_name': 'Hemoglobin',
            'result_value': 14.2,
            'unit': 'g/dL',
            'reference_range': '13.5-17.5',
            'date': datetime.now() - timedelta(days=5),
        })
        LabResult.sudo().create({
            'request_id': lab_req_1.id,
            'analysis_name': 'White Blood Cells',
            'result_value': 7.2,
            'unit': 'K/uL',
            'reference_range': '4.5-11.0',
            'date': datetime.now() - timedelta(days=5),
        })
        LabResult.sudo().create({
            'request_id': lab_req_1.id,
            'analysis_name': 'Platelets',
            'result_value': 245.0,
            'unit': 'K/uL',
            'reference_range': '150-400',
            'date': datetime.now() - timedelta(days=5),
        })
        log('    Added 3 CBC results')
    if lab_req_1.status == 'processing':
        lab_req_1.sudo().action_complete()
        log('    Completed lab request')

    # --- Lab Request 2: Mohamed Amine - Lipid Panel ---
    lab_req_2 = LabRequest.search([
        ('patient_id', '=', patient_mohamed.id),
        ('analysis_type', '=', 'Lipid Panel'),
    ], limit=1)
    if not lab_req_2:
        lab_req_2 = LabRequest.sudo().create({
            'patient_id': patient_mohamed.id,
            'doctor_id': dr_ahmed.id,
            'laboratory_id': lab_sanad.id,
            'analysis_type': 'Lipid Panel',
            'instructions': 'Fasting 12 hours required.',
        })
        log('    Created lab request: Lipid Panel for Mohamed Amine')
    else:
        log('    Reusing lab request: Lipid Panel for Mohamed Amine')

    if lab_req_2.status == 'draft':
        lab_req_2.sudo().action_send()
    if lab_req_2.status == 'sent':
        lab_req_2.sudo().action_accept()
    if lab_req_2.status == 'accepted':
        lab_req_2.sudo().action_start_processing()

    if not lab_req_2.result_ids:
        LabResult.sudo().create({
            'request_id': lab_req_2.id,
            'analysis_name': 'Total Cholesterol',
            'result_value': 220.0,
            'unit': 'mg/dL',
            'reference_range': '125-200',
            'date': datetime.now() - timedelta(days=3),
        })
        LabResult.sudo().create({
            'request_id': lab_req_2.id,
            'analysis_name': 'LDL Cholesterol',
            'result_value': 140.0,
            'unit': 'mg/dL',
            'reference_range': '0-100',
            'date': datetime.now() - timedelta(days=3),
        })
        LabResult.sudo().create({
            'request_id': lab_req_2.id,
            'analysis_name': 'HDL Cholesterol',
            'result_value': 42.0,
            'unit': 'mg/dL',
            'reference_range': '40-60',
            'date': datetime.now() - timedelta(days=3),
        })
        log('    Added 3 lipid panel results')
    if lab_req_2.status == 'processing':
        lab_req_2.sudo().action_complete()

    # --- Lab Request 3: Sara El Idrissi - HbA1c ---
    lab_req_3 = LabRequest.search([
        ('patient_id', '=', patient_sara.id),
        ('analysis_type', '=', 'HbA1c'),
    ], limit=1)
    if not lab_req_3:
        lab_req_3 = LabRequest.sudo().create({
            'patient_id': patient_sara.id,
            'doctor_id': dr_ahmed.id,
            'laboratory_id': lab_al_amal.id,
            'consultation_id': consult_3.id,
            'analysis_type': 'HbA1c',
            'instructions': 'Follow-up HbA1c for diabetes management.',
        })
        log('    Created lab request: HbA1c for Sara El Idrissi')

    if lab_req_3.status == 'draft':
        lab_req_3.sudo().action_send()
    if lab_req_3.status == 'sent':
        lab_req_3.sudo().action_accept()
    if lab_req_3.status == 'accepted':
        lab_req_3.sudo().action_start_processing()

    if not lab_req_3.result_ids:
        LabResult.sudo().create({
            'request_id': lab_req_3.id,
            'analysis_name': 'HbA1c',
            'result_value': 7.8,
            'unit': '%',
            'reference_range': '4.0-5.6',
            'date': datetime.now() - timedelta(days=8),
        })
        log('    Added HbA1c result: 7.8% (elevated)')
    if lab_req_3.status == 'processing':
        lab_req_3.sudo().action_complete()

    # --- Lab Request 4: Yassine Bennani - Routine Blood Work ---
    lab_req_4 = LabRequest.search([
        ('patient_id', '=', patient_yassine.id),
        ('analysis_type', '=', 'Pediatric Routine Panel'),
    ], limit=1)
    if not lab_req_4:
        lab_req_4 = LabRequest.sudo().create({
            'patient_id': patient_yassine.id,
            'doctor_id': dr_youssef.id,
            'laboratory_id': lab_sanad.id,
            'consultation_id': consult_5.id,
            'analysis_type': 'Pediatric Routine Panel',
            'instructions': 'Annual routine blood work for pediatric patient.',
        })
        log('    Created lab request: Pediatric Panel for Yassine Bennani')

    if lab_req_4.status == 'draft':
        lab_req_4.sudo().action_send()
    if lab_req_4.status == 'sent':
        lab_req_4.sudo().action_accept()
    if lab_req_4.status == 'accepted':
        lab_req_4.sudo().action_start_processing()

    if not lab_req_4.result_ids:
        LabResult.sudo().create({
            'request_id': lab_req_4.id,
            'analysis_name': 'Hemoglobin',
            'result_value': 12.8,
            'unit': 'g/dL',
            'reference_range': '11.5-15.5',
            'date': datetime.now() - timedelta(days=2),
        })
        LabResult.sudo().create({
            'request_id': lab_req_4.id,
            'analysis_name': 'Iron',
            'result_value': 85.0,
            'unit': 'mcg/dL',
            'reference_range': '60-170',
            'date': datetime.now() - timedelta(days=2),
        })
        log('    Added 2 pediatric results')
    if lab_req_4.status == 'processing':
        lab_req_4.sudo().action_complete()

    # =========================================================================
    # STEP 8: Create Prescriptions
    # =========================================================================
    log('Step 8: Creating prescriptions...')

    def create_prescription(patient, doctor, medication, dosage, frequency,
                            duration, instructions='', pharmacy=None,
                            consultation=None):
        """Create a prescription."""
        existing = Prescription.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('medication', '=', medication),
        ], limit=1)
        if existing:
            log(f'    Reusing prescription: {medication} for {patient.name}')
            return existing
        vals = {
            'patient_id': patient.id,
            'doctor_id': doctor.id,
            'medication': medication,
            'dosage': dosage,
            'frequency': frequency,
            'duration': duration,
            'instructions': instructions,
        }
        if pharmacy:
            vals['pharmacy_id'] = pharmacy.id
        if consultation:
            vals['consultation_id'] = consultation.id
        rx = Prescription.sudo().create(vals)
        log(f'    Created prescription: {medication} for {patient.name}')
        return rx

    # Mohamed Amine - Hypertension medication
    rx_1 = create_prescription(
        patient=patient_mohamed,
        doctor=dr_ahmed,
        medication='Amlodipine',
        dosage='5mg',
        frequency='Once daily',
        duration='30 days',
        instructions='Take in the morning with food. Avoid grapefruit.',
        pharmacy=pharm_sanad,
        consultation=consult_2,
    )

    # Mohamed Amine - Additional medication
    rx_2 = create_prescription(
        patient=patient_mohamed,
        doctor=dr_ahmed,
        medication='Aspirin',
        dosage='81mg',
        frequency='Once daily',
        duration='30 days',
        instructions='Take with food to reduce stomach irritation.',
        pharmacy=pharm_sanad,
    )

    # Sara El Idrissi - Diabetes medication
    rx_3 = create_prescription(
        patient=patient_sara,
        doctor=dr_ahmed,
        medication='Metformin',
        dosage='500mg',
        frequency='Twice daily',
        duration='30 days',
        instructions='Take with meals. Monitor blood glucose regularly.',
        pharmacy=pharm_al_amal,
        consultation=consult_3,
    )

    # Sara El Idrissi - Cardio referral medication
    rx_4 = create_prescription(
        patient=patient_sara,
        doctor=dr_sara,
        medication='Lisinopril',
        dosage='10mg',
        frequency='Once daily',
        duration='30 days',
        instructions='Blood pressure management. Monitor kidney function.',
        pharmacy=pharm_al_amal,
    )

    # Yassine Bennani - Vitamin supplement
    rx_5 = create_prescription(
        patient=patient_yassine,
        doctor=dr_youssef,
        medication='Vitamin D',
        dosage='400 IU',
        frequency='Once daily',
        duration='90 days',
        instructions='Daily supplement for pediatric patient.',
        pharmacy=pharm_sanad,
    )

    # =========================================================================
    # STEP 9: Process Prescriptions through Pharmacy Workflow
    # =========================================================================
    log('Step 9: Processing prescriptions through pharmacy workflow...')

    # Process Mohamed's prescriptions at Pharmacie SANAD
    for rx in [rx_1, rx_2]:
        if rx.pharmacy_status == 'pending' and rx.pharmacy_id:
            rx.sudo().action_pharmacy_receive()
            log(f'    Received: {rx.medication} for {patient_mohamed.name}')
        if rx.pharmacy_status == 'received':
            rx.sudo().action_pharmacy_prepare()
            log(f'    Prepared: {rx.medication} for {patient_mohamed.name}')
        if rx.pharmacy_status == 'prepared':
            rx.sudo().action_pharmacy_complete()
            log(f'    Completed: {rx.medication} for {patient_mohamed.name}')

    # Process Sara's prescriptions at Pharmacie Al Amal
    for rx in [rx_3, rx_4]:
        if rx.pharmacy_status == 'pending' and rx.pharmacy_id:
            rx.sudo().action_pharmacy_receive()
            log(f'    Received: {rx.medication} for {patient_sara.name}')
        if rx.pharmacy_status == 'received':
            rx.sudo().action_pharmacy_prepare()
            log(f'    Prepared: {rx.medication} for {patient_sara.name}')
        # Keep rx_3 at 'prepared' for demo (not completed yet)

    # Yassine's prescription - still pending at pharmacy
    if rx_5.pharmacy_status == 'pending' and rx_5.pharmacy_id:
        rx_5.sudo().action_pharmacy_receive()
        log(f'    Received: {rx_5.medication} for {patient_yassine.name}')

    # =========================================================================
    # STEP 10: Create Chat Conversations
    # =========================================================================
    log('Step 10: Creating chat conversations...')

    def create_chat(user_a, user_b, conv_type, patient=None):
        """Create a chat conversation."""
        existing = ChatConversation.search([
            ('conversation_type', '=', conv_type),
            ('participant_ids', 'in', [user_a.id]),
            ('participant_ids', 'in', [user_b.id]),
        ], limit=1)
        if existing:
            log(f'    Reusing chat: {user_a.name} <-> {user_b.name}')
            return existing
        vals = {
            'participant_ids': [(6, 0, [user_a.id, user_b.id])],
            'conversation_type': conv_type,
        }
        if patient:
            vals['patient_id'] = patient.id
        conv = ChatConversation.sudo().create(vals)
        log(f'    Created chat: {user_a.name} <-> {user_b.name}')

        # Add a few messages
        conv.sudo().action_post_message(
            f'Hello, this is a demo conversation between {user_a.name} and {user_b.name}.')
        conv.sudo().action_post_message(
            'This is a secure messaging channel for healthcare communication.')
        return conv

    # Dr. Ahmed <-> Mohamed Amine
    conv_1 = create_chat(
        dr_ahmed.user_id, patient_mohamed.user_id,
        'doctor_patient', patient_mohamed)

    # Dr. Ahmed <-> Dr. Sara (lab discussion)
    conv_2 = create_chat(
        dr_ahmed.user_id, dr_sara.user_id,
        'doctor_laboratory')

    # Dr. Ahmed <-> SANAD Lab
    conv_3 = create_chat(
        dr_ahmed.user_id, lab_user_sanad,
        'doctor_laboratory')

    # Dr. Ahmed <-> Pharmacie SANAD
    conv_4 = create_chat(
        dr_ahmed.user_id, pharm_user_sanad,
        'doctor_pharmacy')

    # =========================================================================
    # STEP 11: Validate Everything
    # =========================================================================
    log('')
    log('=' * 60)
    log('VALIDATION REPORT')
    log('=' * 60)

    errors = []

    # Check doctors
    for email in DOCTOR_EMAILS.values():
        user = User.search([('login', '=', email)], limit=1)
        if not user:
            errors.append(f'Missing doctor user: {email}')
        else:
            doctor = Doctor.search([('user_id', '=', user.id)], limit=1)
            if not doctor:
                errors.append(f'Missing doctor profile for: {email}')
            else:
                log(f'  OK: Doctor {doctor.name} (id={doctor.id})')

    # Check patients
    for email in PATIENT_EMAILS.values():
        user = User.search([('login', '=', email)], limit=1)
        if not user:
            errors.append(f'Missing patient user: {email}')
        else:
            patient = Patient.search([('user_id', '=', user.id)], limit=1)
            if not patient:
                errors.append(f'Missing patient profile for: {email}')
            else:
                log(f'  OK: Patient {patient.name} (id={patient.id})')

    # Check care relationships
    for patient, doctor in [
        (patient_mohamed, dr_ahmed),
        (patient_sara, dr_ahmed),
        (patient_sara, dr_sara),
        (patient_yassine, dr_youssef),
    ]:
        rel = CareRel.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('active', '=', True),
        ], limit=1)
        if not rel:
            errors.append(f'Missing care rel: {patient.name} <-> {doctor.name}')
        else:
            log(f'  OK: Care relationship {patient.name} <-> {doctor.name} (id={rel.id})')

    # Check consultations
    consultations = Consultation.search([])
    log(f'  OK: {len(consultations)} consultations created')
    for c in consultations:
        log(f'    - {c.patient_id.name}: {c.reason} ({c.date.date()})')

    # Check medical records (auto-provisioned)
    records = MedicalRecord.search([])
    log(f'  OK: {len(records)} medical records auto-provisioned')
    for r in records:
        log(f'    - Patient: {r.patient_id.name}, Consultations: {r.consultation_count}, '
            f'Prescriptions: {r.prescription_count}')

    # Check lab requests
    lab_reqs = LabRequest.search([])
    log(f'  OK: {len(lab_reqs)} lab requests created')
    for lr in lab_reqs:
        log(f'    - {lr.patient_id.name}: {lr.analysis_type} [{lr.status}]')

    # Check lab results
    lab_results = LabResult.search([])
    log(f'  OK: {len(lab_results)} lab results created')
    for lr in lab_results:
        log(f'    - {lr.analysis_name}: {lr.result_value} {lr.unit} [{lr.request_id.patient_id.name}]')

    # Check prescriptions
    prescriptions = Prescription.search([])
    log(f'  OK: {len(prescriptions)} prescriptions created')
    for p in prescriptions:
        log(f'    - {p.patient_id.name}: {p.medication} [{p.pharmacy_status}]')

    # Check chat conversations
    conversations = ChatConversation.search([])
    log(f'  OK: {len(conversations)} chat conversations created')

    # Check organizations
    lab_orgs = LabOrg.search([])
    pharm_orgs = PharmacyOrg.search([])
    log(f'  OK: {len(lab_orgs)} lab organizations')
    log(f'  OK: {len(pharm_orgs)} pharmacy organizations')

    # Check lab staff linking
    for lab_user in [lab_user_sanad, lab_user_al_amal]:
        user = User.search([('login', '=', lab_user.login)], limit=1)
        linked_labs = LabOrg.search([('user_ids', 'in', [user.id])])
        log(f'  OK: Lab user {user.name} linked to {len(linked_labs)} lab(s)')

    # Check pharmacy staff linking
    for pharm_user in [pharm_user_sanad, pharm_user_al_amal]:
        user = User.search([('login', '=', pharm_user.login)], limit=1)
        linked_pharms = PharmacyOrg.search([('user_ids', 'in', [user.id])])
        log(f'  OK: Pharmacy user {user.name} linked to {len(linked_pharms)} pharmacy(ies)')

    log('')
    if errors:
        log('ERRORS FOUND:')
        for e in errors:
            log(f'  FAIL: {e}')
        return False
    else:
        log('ALL VALIDATIONS PASSED!')
        log('')
        log('Demo dataset summary:')
        log(f'  - {len(DOCTOR_EMAILS)} doctors with user accounts')
        log(f'  - {len(PATIENT_EMAILS)} patients with user accounts')
        log(f'  - {len(LAB_EMAILS)} lab staff users')
        log(f'  - {len(PHARMACY_EMAILS)} pharmacy staff users')
        log(f'  - {len(CareRel.search([]))} active care relationships')
        log(f'  - {len(consultations)} consultations')
        log(f'  - {len(records)} medical records')
        log(f'  - {len(lab_reqs)} lab requests')
        log(f'  - {len(lab_results)} lab results')
        log(f'  - {len(prescriptions)} prescriptions')
        log(f'  - {len(conversations)} chat conversations')
        return True


# ---------------------------------------------------------------------------
# Entry point for direct execution
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('This script must be run inside an Odoo shell environment.')
    print('Usage:')
    print('  docker exec -it sanad_odoo odoo shell -d sanad_db -c /etc/odoo/odoo.conf')
    print('  >>> exec(open("/mnt/extra-addons/scripts/create_demo_data.py").read())')
    print('')
    print('Or directly in odoo-bin shell:')
    print('  odoo shell -d sanad_db --addons-path=/mnt/extra-addons')
    print('  >>> exec(open("scripts/create_demo_data.py").read())')
