#!/usr/bin/env python3
"""
SANAD Comprehensive Demo Data Creator
======================================
Creates a complete, logically connected, realistic demo dataset.
Works with existing data - idempotent (safe to run multiple times).

Usage:
    docker exec -it sanad_odoo odoo shell -d sanad_db -c /etc/odoo/odoo.conf
    >>> exec(open('/mnt/extra-addons/scripts/sanad_demo_data.py').read())
    >>> create_all(env)
"""

from datetime import date, datetime, timedelta


def log(msg):
    print(f'[SANAD] {msg}')


def commit_step(env, step_name):
    """Commit current step so data survives even if later steps fail."""
    env.cr.commit()
    log(f'  [COMMITTED: {step_name}]')


def create_all(env):
    """Create the complete SANAD demo dataset."""

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

    group_admin = env.ref('sanad_core.group_sanad_admin')
    group_doctor = env.ref('sanad_core.group_sanad_doctor')
    group_patient = env.ref('sanad_core.group_sanad_patient')
    group_lab = env.ref('sanad_core.group_sanad_laboratory')
    group_pharmacy = env.ref('sanad_core.group_sanad_pharmacy')

    log('=' * 60)
    log('SANAD DEMO DATA CREATION')
    log('=' * 60)

    # =================================================================
    # STEP 1: SPECIALTIES (reuse existing, create missing)
    # =================================================================
    log('\n--- Step 1: Specialties ---')

    spec_general = Specialty.search([('name', 'ilike', 'General')], limit=1)
    if not spec_general:
        spec_general = Specialty.create({'name': 'General Medicine', 'code': 'GEN'})
        log('  Created: General Medicine')
    else:
        log(f'  Reusing: General Medicine (id={spec_general.id})')

    spec_cardio = Specialty.search([('name', 'ilike', 'Cardiol')], limit=1)
    if not spec_cardio:
        spec_cardio = Specialty.create({'name': 'Cardiology', 'code': 'CARDIO'})
        log('  Created: Cardiology')
    else:
        log(f'  Reusing: Cardiology (id={spec_cardio.id})')

    spec_pedia = Specialty.search([('name', 'ilike', 'Pediatr')], limit=1)
    if not spec_pedia:
        spec_pedia = Specialty.create({'name': 'Pediatrics', 'code': 'PEDIA'})
        log('  Created: Pediatrics')
    else:
        log(f'  Reusing: Pediatrics (id={spec_pedia.id})')

    spec_internal = Specialty.search([('name', 'ilike', 'Internal')], limit=1)
    if not spec_internal:
        spec_internal = Specialty.create({'name': 'Internal Medicine', 'code': 'INTMED'})
        log('  Created: Internal Medicine')
    else:
        log(f'  Reusing: Internal Medicine (id={spec_internal.id})')

    commit_step(env, 'Step 1: Specialties')

    # =================================================================
    # STEP 2: ORGANIZATIONS
    # =================================================================
    log('\n--- Step 2: Organizations ---')

    # Cabinets
    cabinet_sanad = Cabinet.search([('name', 'ilike', 'SANAD')], limit=1)
    if not cabinet_sanad:
        cabinet_sanad = Cabinet.create({
            'name': 'Cabinet Médical SANAD',
            'phone': '+212 5 22 00 00 01',
            'email': 'cabinet@sanad-health.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created: Cabinet Médical SANAD')
    else:
        log(f'  Reusing: {cabinet_sanad.name} (id={cabinet_sanad.id})')

    cabinet_al_amal = Cabinet.search([('name', 'ilike', 'Al Amal')], limit=1)
    if not cabinet_al_amal:
        cabinet_al_amal = Cabinet.create({
            'name': 'Cabinet Al Amal',
            'phone': '+212 5 22 00 00 02',
            'email': 'cabinet@alamal.example.com',
            'address': 'Rabat, Morocco',
        })
        log('  Created: Cabinet Al Amal')
    else:
        log(f'  Reusing: {cabinet_al_amal.name} (id={cabinet_al_amal.id})')

    # Laboratories
    lab_central = LabOrg.search([('name', 'ilike', 'Central')], limit=1)
    if not lab_central:
        lab_central = LabOrg.create({
            'name': 'Laboratoire Central SANAD',
            'phone': '+212 5 22 00 00 10',
            'email': 'contact@labcentral.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created: Laboratoire Central SANAD')
    else:
        log(f'  Reusing: {lab_central.name} (id={lab_central.id})')

    lab_biomed = LabOrg.search([('name', 'ilike', 'BioMed')], limit=1)
    if not lab_biomed:
        lab_biomed = LabOrg.create({
            'name': 'Laboratoire BioMed',
            'phone': '+212 5 22 00 00 11',
            'email': 'contact@biomed.example.com',
            'address': 'Rabat, Morocco',
        })
        log('  Created: Laboratoire BioMed')
    else:
        log(f'  Reusing: {lab_biomed.name} (id={lab_biomed.id})')

    # Pharmacies
    pharm_sanad = PharmacyOrg.search([('name', 'ilike', 'SANAD')], limit=1)
    if not pharm_sanad:
        pharm_sanad = PharmacyOrg.create({
            'name': 'Pharmacie SANAD',
            'phone': '+212 5 22 00 00 20',
            'email': 'contact@pharmaciesanad.example.com',
            'address': 'Casablanca, Morocco',
        })
        log('  Created: Pharmacie SANAD')
    else:
        log(f'  Reusing: {pharm_sanad.name} (id={pharm_sanad.id})')

    pharm_al_amal = PharmacyOrg.search([('name', 'ilike', 'Pharmacie Al Amal')], limit=1)
    if not pharm_al_amal:
        pharm_al_amal = PharmacyOrg.create({
            'name': 'Pharmacie Al Amal',
            'phone': '+212 5 22 00 00 21',
            'email': 'contact@pharmaciealamal.example.com',
            'address': 'Rabat, Morocco',
        })
        log('  Created: Pharmacie Al Amal')
    else:
        log(f'  Reusing: {pharm_al_amal.name} (id={pharm_al_amal.id})')

    commit_step(env, 'Step 2: Organizations')

    # =================================================================
    # STEP 3: DOCTORS (reuse existing Dr. Ahmed, create new ones)
    # =================================================================
    log('\n--- Step 3: Doctors ---')

    def get_or_create_doctor(name, email, phone, specialty, license_num, cabinet, info=''):
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({'name': name, 'email': email, 'phone': phone, 'company_type': 'person'})
            log(f'    + Partner: {name}')
        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name, 'login': email, 'partner_id': partner.id,
            })
            group_doctor.write({'user_ids': [(4, user.id)]})
            log(f'    + User: {email}')
        doctor = Doctor.search([('partner_id', '=', partner.id)], limit=1)
        if not doctor:
            doctor = Doctor.create({
                'partner_id': partner.id, 'user_id': user.id,
                'specialty_id': specialty.id, 'license_number': license_num,
                'cabinet_id': cabinet.id, 'professional_info': info,
            })
            log(f'    + Doctor: {name}')
        else:
            log(f'    Reusing doctor: {name} (id={doctor.id})')
            if not doctor.cabinet_id:
                doctor.write({'cabinet_id': cabinet.id, 'specialty_id': specialty.id})
        return doctor

    # Existing Dr. Ahmed - update if needed
    existing_ahmed = User.search([('login', '=', 'ahmed.benali@test.sanad')], limit=1)
    if existing_ahmed:
        dr_ahmed = Doctor.search([('user_id', '=', existing_ahmed.id)], limit=1)
        if dr_ahmed:
            if not dr_ahmed.specialty_id:
                dr_ahmed.write({'specialty_id': spec_general.id, 'cabinet_id': cabinet_sanad.id})
            log(f'  Reusing: Dr. Ahmed Benali (id={dr_ahmed.id})')
        else:
            dr_ahmed = Doctor.create({
                'partner_id': existing_ahmed.partner_id.id, 'user_id': existing_ahmed.id,
                'specialty_id': spec_general.id, 'license_number': 'SANAD-LIC-001',
                'cabinet_id': cabinet_sanad.id,
                'professional_info': 'General practitioner, 10 years experience.',
            })
            log(f'  Created: Dr. Ahmed Benali')
    else:
        dr_ahmed = get_or_create_doctor(
            'Dr. Ahmed Benali', 'ahmed.benali@test.sanad', '+212 6 11 22 33 01',
            spec_general, 'SANAD-LIC-001', cabinet_sanad,
            'General practitioner, 10 years experience.')

    dr_sara = get_or_create_doctor(
        'Dr. Sara Alaoui', 'sara.alaoui@test.sanad', '+212 6 11 22 33 02',
        spec_cardio, 'SANAD-LIC-002', cabinet_sanad,
        'Cardiologist, 12 years experience in interventional cardiology.')

    dr_youssef = get_or_create_doctor(
        'Dr. Youssef Amrani', 'youssef.amrani@test.sanad', '+212 6 11 22 33 03',
        spec_pedia, 'SANAD-LIC-003', cabinet_al_amal,
        'Pediatrician, 8 years experience in childhood vaccinations.')

    dr_lina = get_or_create_doctor(
        'Dr. Lina El Mansouri', 'lina.mansouri@test.sanad', '+212 6 11 22 33 04',
        spec_internal, 'SANAD-LIC-004', cabinet_al_amal,
        'Internal medicine specialist, 15 years experience.')

    commit_step(env, 'Step 3: Doctors')

    # =================================================================
    # STEP 4: LAB/PHARMACY STAFF (reuse existing, create + link)
    # =================================================================
    log('\n--- Step 4: Lab/Pharmacy Staff ---')

    def get_or_create_staff(name, email, phone, group, org):
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({'name': name, 'email': email, 'phone': phone, 'company_type': 'person'})
            log(f'    + Staff partner: {name}')
        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name, 'login': email, 'partner_id': partner.id,
            })
            group.write({'user_ids': [(4, user.id)]})
            log(f'    + Staff user: {email}')
        # CRITICAL: Link user to org via direct SQL to avoid ORM caching issues
        if org:
            org_model = org._name
            table = org_model.replace('.', '_')
            rel_table = f'res_users_{table}_rel'
            cr = env.cr
            cr.execute(
                f"INSERT INTO {rel_table} ({table}_id, res_users_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (org.id, user.id))
            env.invalidate_all()
            log(f'    Linked {name} -> {org.name}')
        return user

    # Reuse existing lab.test and pharmacy.test, link to proper orgs
    lab_user_central = get_or_create_staff(
        'Lab Central Technician', 'lab.test@sanad.local', '+212 6 44 55 66 01',
        group_lab, lab_central)

    lab_user_biomed = get_or_create_staff(
        'BioMed Technician', 'lab.biomed@test.sanad', '+212 6 44 55 66 02',
        group_lab, lab_biomed)

    pharm_user_sanad = get_or_create_staff(
        'SANAD Pharmacist', 'pharmacy.test@sanad.local', '+212 6 77 88 99 01',
        group_pharmacy, pharm_sanad)

    pharm_user_al_amal = get_or_create_staff(
        'Al Amal Pharmacist', 'pharmacy.alamal@test.sanad', '+212 6 77 88 99 02',
        group_pharmacy, pharm_al_amal)

    commit_step(env, 'Step 4: Lab/Pharmacy Staff')

    # =================================================================
    # STEP 5: PATIENTS (reuse existing, create new)
    # =================================================================
    log('\n--- Step 5: Patients ---')

    def get_or_create_patient(name, email, phone, birth_date, gender, blood_group,
                               allergies='', chronic='', emerg_name='', emerg_phone='',
                               emerg_relation=''):
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({'name': name, 'email': email, 'phone': phone, 'company_type': 'person'})
            log(f'    + Patient partner: {name}')
        user = User.search([('login', '=', email)], limit=1)
        if not user:
            user = User.create({
                'name': name, 'login': email, 'partner_id': partner.id,
            })
            group_patient.write({'user_ids': [(4, user.id)]})
            log(f'    + Patient user: {email}')
        patient = Patient.search([('partner_id', '=', partner.id)], limit=1)
        if not patient:
            patient = Patient.create({
                'partner_id': partner.id, 'user_id': user.id,
                'birth_date': birth_date, 'gender': gender, 'blood_group': blood_group,
                'allergies': allergies, 'chronic_diseases': chronic,
                'emergency_contact_name': emerg_name,
                'emergency_contact_phone': emerg_phone,
                'emergency_contact_relation': emerg_relation,
            })
            log(f'    + Patient: {name}')
        else:
            log(f'    Reusing patient: {name} (id={patient.id})')
        return patient

    # Reuse existing Patient Test
    existing_patient = User.search([('login', '=', 'patient.test@sanad.local')], limit=1)
    if existing_patient:
        patient_mohamed = Patient.search([('user_id', '=', existing_patient.id)], limit=1)
        if patient_mohamed:
            log(f'  Reusing: Mohamed El Idrissi (id={patient_mohamed.id})')
        else:
            patient_mohamed = Patient.create({
                'partner_id': existing_patient.partner_id.id, 'user_id': existing_patient.id,
                'birth_date': date(1990, 5, 15), 'gender': 'male', 'blood_group': 'a_pos',
                'allergies': 'Aspirin', 'chronic_diseases': 'Hypertension',
                'emergency_contact_name': 'Fatima El Idrissi',
                'emergency_contact_phone': '+212 6 99 88 77 66',
                'emergency_contact_relation': 'Wife',
            })
            log(f'  Created patient profile for Mohamed El Idrissi')
    else:
        patient_mohamed = get_or_create_patient(
            'Mohamed El Idrissi', 'patient.test@sanad.local', '+212 6 10 20 30 40',
            date(1990, 5, 15), 'male', 'a_pos',
            'Aspirin', 'Hypertension',
            'Fatima El Idrissi', '+212 6 99 88 77 66', 'Wife')

    patient_sara = get_or_create_patient(
        'Sara Bennani', 'sara.bennani@test.sanad', '+212 6 20 30 40 50',
        date(1985, 8, 22), 'female', 'b_pos',
        'None', 'Type 2 Diabetes',
        'Omar Bennani', '+212 6 77 88 99 00', 'Husband')

    patient_omar = get_or_create_patient(
        'Omar Tazi', 'omar.tazi@test.sanad', '+212 6 30 40 50 60',
        date(1978, 12, 3), 'male', 'o_neg',
        'Penicillin', 'Asthma',
        'Khadija Tazi', '+212 6 66 55 44 33', 'Wife')

    patient_yasmine = get_or_create_patient(
        'Yasmine Amrani', 'yasmine.amrani@test.sanad', '+212 6 40 50 60 70',
        date(2015, 3, 10), 'female', 'a_neg',
        'Peanuts', 'None',
        'Rachid Amrani', '+212 6 55 44 33 22', 'Father')

    commit_step(env, 'Step 5: Patients')

    # =================================================================
    # STEP 6: CARE RELATIONSHIPS
    # =================================================================
    log('\n--- Step 6: Care Relationships ---')

    def create_care_rel(patient, doctor, rel_type='primary', notes=''):
        existing = CareRel.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('relationship_type', '=', rel_type),
        ], limit=1)
        if existing:
            log(f'    Reusing: {patient.name} <-> {doctor.name} ({rel_type})')
            return existing
        rel = CareRel.create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'relationship_type': rel_type,
            'start_date': date(2026, 1, 1),
            'notes': notes,
        })
        log(f'    + Care rel: {patient.name} <-> {doctor.name} ({rel_type})')
        return rel

    # Mohamed El Idrissi -> Dr. Ahmed Benali (primary - hypertension)
    create_care_rel(patient_mohamed, dr_ahmed, 'primary', 'Primary care - hypertension management')

    # Sara Bennani -> Dr. Ahmed Benali (consulting - diabetes)
    create_care_rel(patient_sara, dr_ahmed, 'consulting', 'General consultation - diabetes management')

    # Sara Bennani -> Dr. Sara Alaoui (primary - cardiology)
    create_care_rel(patient_sara, dr_sara, 'primary', 'Cardiology - cardiac evaluation for diabetic patient')

    # Omar Tazi -> Dr. Ahmed Benali (primary - asthma)
    create_care_rel(patient_omar, dr_ahmed, 'primary', 'Primary care - asthma management')

    # Omar Tazi -> Dr. Lina El Mansouri (consulting - internal medicine)
    create_care_rel(patient_omar, dr_lina, 'consulting', 'Internal medicine consultation')

    # Yasmine Amrani -> Dr. Youssef Amrani (primary - pediatric)
    create_care_rel(patient_yasmine, dr_youssef, 'primary', 'Pediatric care - regular checkups')

    commit_step(env, 'Step 6: Care Relationships')

    # =================================================================
    # STEP 7: CONSULTATIONS
    # =================================================================
    log('\n--- Step 7: Consultations ---')

    def create_consultation(patient, doctor, reason, symptoms='', observations='',
                            report='', offset_days=0):
        existing = Consultation.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('reason', '=', reason),
        ], limit=1)
        if existing:
            log(f'    Reusing: {reason} for {patient.name}')
            return existing
        c = Consultation.sudo().create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'reason': reason, 'symptoms': symptoms,
            'observations': observations, 'report': report,
            'date': datetime.now() - timedelta(days=offset_days),
        })
        log(f'    + Consultation: {reason} for {patient.name}')
        return c

    # --- MAIN JOURNEY: Mohamed El Idrissi - Hypertension Investigation ---
    c1 = create_consultation(
        patient_mohamed, dr_ahmed,
        reason='Persistent fatigue and headaches',
        symptoms='Chronic fatigue, recurring headaches, occasional dizziness, '
                 'difficulty concentrating for 3 weeks',
        observations='Blood pressure: 150/95 mmHg (elevated). Heart rate: 78 bpm. '
                     'BMI: 27. Patient reports high-stress work environment and '
                     'poor sleep quality. No family history of cardiovascular disease. '
                     'Possible iron deficiency anemia recommended for investigation.',
        report='<p><strong>Preliminary Assessment:</strong> Stage 1 Hypertension with '
               'suspected iron deficiency. Recommend CBC, Ferritin, Iron, and Vitamin B12 '
               'tests to rule out anemia as contributing factor to fatigue.</p>',
        offset_days=21,
    )

    c2 = create_consultation(
        patient_mohamed, dr_ahmed,
        reason='Hypertension follow-up and lab review',
        symptoms='Reduced headaches, persistent fatigue',
        observations='Blood pressure: 138/88 mmHg (improved). Patient started daily walking. '
                     'Lab results reviewed: Ferritin low at 8 ng/mL, Iron borderline. '
                     'Vitamin B12 within normal range.',
        report='<p><strong>Follow-up:</strong> Blood pressure improving with lifestyle changes. '
               'Iron supplementation recommended. Continue monitoring. '
               'Follow-up in 4 weeks.</p>',
        offset_days=7,
    )

    # Sara Bennani - Diabetes + Cardiology
    c3 = create_consultation(
        patient_sara, dr_ahmed,
        reason='Diabetes management review',
        symptoms='Increased thirst, frequent urination, fatigue',
        observations='HbA1c: 8.2% (suboptimal). Current: Metformin 500mg twice daily. '
                     'Referred to cardiology for baseline cardiac evaluation due to '
                     '10-year diabetes duration.',
        report='<p><strong>Assessment:</strong> Type 2 Diabetes with suboptimal glycemic control. '
               'Cardiology referral for cardiac assessment. HbA1c monitoring required.</p>',
        offset_days=14,
    )

    c4 = create_consultation(
        patient_sara, dr_sara,
        reason='Cardiac evaluation for diabetes',
        symptoms='None cardiac-specific',
        observations='ECG: Normal sinus rhythm. Echocardiogram: Normal LV function, '
                     'EF 60%. No valvular abnormalities. Blood pressure: 125/80 mmHg.',
        report='<p><strong>Cardiac Assessment:</strong> No evidence of diabetic cardiomyopathy. '
               'Cardiac function normal. Continue diabetes management with primary physician. '
               'Annual cardiac follow-up recommended.</p>',
        offset_days=10,
    )

    # Omar Tazi - Asthma
    c5 = create_consultation(
        patient_omar, dr_ahmed,
        reason='Asthma exacerbation',
        symptoms='Wheezing, shortness of breath, chest tightness, nighttime cough',
        observations='SpO2: 96%. Mild wheezing on auscultation. Peak flow: 350 L/min '
                     '(personal best 450). Trigger identified: dust exposure at work.',
        report='<p><strong>Assessment:</strong> Mild asthma exacerbation triggered by '
               'occupational dust exposure. Adjust inhaler therapy. '
               'Workplace exposure assessment recommended.</p>',
        offset_days=3,
    )

    # Yasmine Amrani - Pediatric checkup
    c6 = create_consultation(
        patient_yasmine, dr_youssef,
        reason='Annual pediatric checkup',
        symptoms='None - routine visit',
        observations='Height: 152 cm (75th percentile). Weight: 42 kg (70th percentile). '
                     'BMI normal. Vaccination schedule up to date. '
                     'No concerns reported by father.',
        report='<p><strong>Assessment:</strong> Normal growth and development. '
               'All milestones met. Continue regular annual checkups.</p>',
        offset_days=5,
    )

    commit_step(env, 'Step 7: Consultations')

    # =================================================================
    # STEP 8: LAB REQUESTS & RESULTS
    # =================================================================
    log('\n--- Step 8: Lab Requests & Results ---')

    def create_lab_request(patient, doctor, lab, analysis, instructions='',
                           consultation=None, status_to='completed'):
        existing = LabRequest.search([
            ('patient_id', '=', patient.id),
            ('analysis_type', '=', analysis),
        ], limit=1)
        if existing:
            log(f'    Reusing: {analysis} for {patient.name}')
            return existing
        req = LabRequest.sudo().create({
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'laboratory_id': lab.id, 'analysis_type': analysis,
            'instructions': instructions,
            'consultation_id': consultation.id if consultation else False,
        })
        log(f'    + Lab request: {analysis} for {patient.name} -> {lab.name}')
        # Process through workflow
        if req.status == 'draft':
            req.sudo().action_send()
        if req.status == 'sent':
            req.sudo().action_accept()
        if req.status == 'accepted':
            req.sudo().action_start_processing()
        return req

    def add_result(req, name, value, unit, ref_range, days_ago=0):
        if req.result_ids.filtered(lambda r: r.analysis_name == name):
            return
        LabResult.sudo().create({
            'request_id': req.id, 'analysis_name': name,
            'result_value': value, 'unit': unit,
            'reference_range': ref_range,
            'date': datetime.now() - timedelta(days=days_ago),
        })

    # --- Mohamed El Idrissi: Complete Blood Count ---
    req1 = create_lab_request(
        patient_mohamed, dr_ahmed, lab_central,
        'Complete Blood Count',
        'Fasting required. Patient on hypertension medication. '
        'Suspected iron deficiency anemia.',
        consultation=c1,
    )
    add_result(req1, 'Hemoglobin', 11.2, 'g/dL', '13.5-17.5', 18)
    add_result(req1, 'Hematocrit', 34.5, '%', '38.3-48.6', 18)
    add_result(req1, 'White Blood Cells', 7.2, 'K/uL', '4.5-11.0', 18)
    add_result(req1, 'Platelets', 245.0, 'K/uL', '150-400', 18)
    add_result(req1, 'Red Blood Cells', 4.1, 'M/uL', '4.5-5.5', 18)
    if req1.status == 'processing':
        req1.sudo().action_complete()
        log('    Completed: CBC for Mohamed')

    # --- Mohamed El Idrissi: Iron Studies ---
    req2 = create_lab_request(
        patient_mohamed, dr_ahmed, lab_central,
        'Iron Studies',
        'Fasting 12 hours required. Follow-up for suspected iron deficiency.',
        consultation=c2,
    )
    add_result(req2, 'Ferritin', 8.0, 'ng/mL', '12-300', 5)
    add_result(req2, 'Serum Iron', 45.0, 'mcg/dL', '60-170', 5)
    add_result(req2, 'TIBC', 420.0, 'mcg/dL', '250-370', 5)
    add_result(req2, 'Transferrin Saturation', 10.7, '%', '20-50', 5)
    if req2.status == 'processing':
        req2.sudo().action_complete()
        log('    Completed: Iron Studies for Mohamed')

    # --- Mohamed El Idrissi: Lipid Panel ---
    req3 = create_lab_request(
        patient_mohamed, dr_ahmed, lab_central,
        'Lipid Panel',
        'Fasting 12 hours. Cardiovascular risk assessment.',
    )
    add_result(req3, 'Total Cholesterol', 220.0, 'mg/dL', '125-200', 3)
    add_result(req3, 'LDL Cholesterol', 140.0, 'mg/dL', '0-100', 3)
    add_result(req3, 'HDL Cholesterol', 42.0, 'mg/dL', '40-60', 3)
    add_result(req3, 'Triglycerides', 180.0, 'mg/dL', '0-150', 3)
    if req3.status == 'processing':
        req3.sudo().action_complete()
        log('    Completed: Lipid Panel for Mohamed')

    # --- Sara Bennani: HbA1c ---
    req4 = create_lab_request(
        patient_sara, dr_ahmed, lab_biomed,
        'HbA1c',
        'Follow-up HbA1c for diabetes management. Current: 8.2%.',
        consultation=c3,
    )
    add_result(req4, 'HbA1c', 7.8, '%', '4.0-5.6', 10)
    if req4.status == 'processing':
        req4.sudo().action_complete()
        log('    Completed: HbA1c for Sara')

    # --- Sara Bennani: Lipid Panel ---
    req5 = create_lab_request(
        patient_sara, dr_sara, lab_biomed,
        'Lipid Panel - Cardiology',
        'Cardiovascular risk assessment for diabetic patient.',
        consultation=c4,
    )
    add_result(req5, 'Total Cholesterol', 235.0, 'mg/dL', '125-200', 8)
    add_result(req5, 'LDL Cholesterol', 150.0, 'mg/dL', '0-100', 8)
    add_result(req5, 'HDL Cholesterol', 38.0, 'mg/dL', '40-60', 8)
    if req5.status == 'processing':
        req5.sudo().action_complete()
        log('    Completed: Lipid Panel for Sara')

    # --- Omar Tazi: Pulmonary Function ---
    req6 = create_lab_request(
        patient_omar, dr_ahmed, lab_central,
        'Pulmonary Function Test',
        'Asthma assessment. Baseline spirometry.',
        consultation=c5,
    )
    add_result(req6, 'FEV1', 2.8, 'L', '3.0-4.0', 2)
    add_result(req6, 'FVC', 3.5, 'L', '3.5-4.5', 2)
    add_result(req6, 'FEV1/FVC Ratio', 80.0, '%', '70-100', 2)
    if req6.status == 'processing':
        req6.sudo().action_complete()
        log('    Completed: PFT for Omar')

    # --- Yasmine Amrani: Pediatric Panel ---
    req7 = create_lab_request(
        patient_yasmine, dr_youssef, lab_biomed,
        'Pediatric Routine Panel',
        'Annual checkup blood work.',
        consultation=c6,
    )
    add_result(req7, 'Hemoglobin', 12.8, 'g/dL', '11.5-15.5', 4)
    add_result(req7, 'Iron', 85.0, 'mcg/dL', '60-170', 4)
    add_result(req7, 'Glucose', 88.0, 'mg/dL', '70-100', 4)
    if req7.status == 'processing':
        req7.sudo().action_complete()
        log('    Completed: Pediatric Panel for Yasmine')

    commit_step(env, 'Step 8: Lab Requests & Results')

    # =================================================================
    # STEP 9: PRESCRIPTIONS
    # =================================================================
    log('\n--- Step 9: Prescriptions ---')

    def create_prescription(patient, doctor, medication, dosage, freq, duration,
                            instructions='', pharmacy=None, consultation=None):
        existing = Prescription.search([
            ('patient_id', '=', patient.id),
            ('doctor_id', '=', doctor.id),
            ('medication', '=', medication),
        ], limit=1)
        if existing:
            log(f'    Reusing: {medication} for {patient.name}')
            return existing
        vals = {
            'patient_id': patient.id, 'doctor_id': doctor.id,
            'medication': medication, 'dosage': dosage,
            'frequency': freq, 'duration': duration,
            'instructions': instructions,
        }
        if pharmacy:
            vals['pharmacy_id'] = pharmacy.id
        if consultation:
            vals['consultation_id'] = consultation.id
        rx = Prescription.sudo().create(vals)
        log(f'    + Prescription: {medication} for {patient.name}')
        return rx

    # Mohamed El Idrissi - Iron + Blood pressure
    rx1 = create_prescription(
        patient_mohamed, dr_ahmed,
        'Ferrous Sulfate', '325mg', 'Once daily', '30 days',
        'Take on empty stomach with vitamin C for better absorption. '
        'May cause dark stools - this is normal.',
        pharmacy=pharm_sanad, consultation=c2,
    )

    rx2 = create_prescription(
        patient_mohamed, dr_ahmed,
        'Amlodipine', '5mg', 'Once daily', '30 days',
        'Take in the morning. Avoid grapefruit. Monitor for dizziness.',
        pharmacy=pharm_sanad, consultation=c2,
    )

    rx3 = create_prescription(
        patient_mohamed, dr_ahmed,
        'Aspirin', '81mg', 'Once daily', '30 days',
        'Take with food to reduce stomach irritation.',
        pharmacy=pharm_sanad,
    )

    # Sara Bennani - Diabetes + Cardio
    rx4 = create_prescription(
        patient_sara, dr_ahmed,
        'Metformin', '500mg', 'Twice daily', '30 days',
        'Take with meals. Monitor blood glucose regularly. '
        'Report any unusual muscle pain.',
        pharmacy=pharm_al_amal, consultation=c3,
    )

    rx5 = create_prescription(
        patient_sara, dr_sara,
        'Lisinopril', '10mg', 'Once daily', '30 days',
        'Blood pressure management. Monitor kidney function. '
        'Report persistent cough.',
        pharmacy=pharm_al_amal,
    )

    # Omar Tazi - Asthma
    rx6 = create_prescription(
        patient_omar, dr_ahmed,
        'Salbutamol Inhaler', '100mcg', '2 puffs as needed', '30 days',
        'Use rescue inhaler for acute symptoms. Shake well before use. '
        'Rinse mouth after use.',
        pharmacy=pharm_sanad, consultation=c5,
    )

    rx7 = create_prescription(
        patient_omar, dr_ahmed,
        'Fluticasone Inhaler', '250mcg', '2 puffs twice daily', '30 days',
        'Maintenance inhaler for asthma control. Use consistently even when feeling well.',
        pharmacy=pharm_sanad,
    )

    # Yasmine Amrani - Vitamin
    rx8 = create_prescription(
        patient_yasmine, dr_youssef,
        'Vitamin D', '400 IU', 'Once daily', '90 days',
        'Daily supplement for pediatric patient. Take with food.',
        pharmacy=pharm_al_amal,
    )

    commit_step(env, 'Step 9: Prescriptions')

    # =================================================================
    # STEP 10: PHARMACY WORKFLOW
    # =================================================================
    log('\n--- Step 10: Pharmacy Workflow ---')

    def process_pharmacy(rx, target_status='completed'):
        """Process prescription through pharmacy workflow to target status."""
        if rx.pharmacy_status == 'pending' and rx.pharmacy_id:
            rx.sudo().action_pharmacy_receive()
        if rx.pharmacy_status == 'received' and target_status in ('prepared', 'completed'):
            rx.sudo().action_pharmacy_prepare()
        if rx.pharmacy_status == 'prepared' and target_status == 'completed':
            rx.sudo().action_pharmacy_complete()

    # Mohamed's prescriptions: complete
    for rx in [rx1, rx2, rx3]:
        process_pharmacy(rx, 'completed')
        log(f'    Completed: {rx.medication} for Mohamed')

    # Sara's prescriptions: Metformin completed, Lisinopril prepared (in progress)
    process_pharmacy(rx4, 'completed')
    log(f'    Completed: {rx4.medication} for Sara')
    process_pharmacy(rx5, 'prepared')
    log(f'    Prepared: {rx5.medication} for Sara (pending completion)')

    # Omar's prescriptions: Salbutamol completed, Fluticasone received
    process_pharmacy(rx6, 'completed')
    log(f'    Completed: {rx6.medication} for Omar')
    process_pharmacy(rx7, 'received')
    log(f'    Received: {rx7.medication} for Omar (pending preparation)')

    # Yasmine's prescription: received only
    process_pharmacy(rx8, 'received')
    log(f'    Received: {rx8.medication} for Yasmine')

    commit_step(env, 'Step 10: Pharmacy Workflow')

    # =================================================================
    # STEP 11: CHAT CONVERSATIONS
    # =================================================================
    log('\n--- Step 11: Chat Conversations ---')

    def create_chat(user_a, user_b, conv_type, patient=None):
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
        try:
            conv = ChatConversation.sudo().create(vals)
            conv.sudo().action_post_message(
                f'Demo conversation: {user_a.name} <-> {user_b.name}')
            log(f'    + Chat: {user_a.name} <-> {user_b.name}')
            return conv
        except Exception as e:
            log(f'    [WARN] Could not create chat {user_a.name} <-> {user_b.name}: {e}')
            return None

    create_chat(dr_ahmed.user_id, patient_mohamed.user_id, 'doctor_patient', patient_mohamed)
    create_chat(dr_ahmed.user_id, patient_sara.user_id, 'doctor_patient', patient_sara)
    create_chat(dr_ahmed.user_id, lab_user_central, 'doctor_laboratory')
    create_chat(dr_ahmed.user_id, pharm_user_sanad, 'doctor_pharmacy')

    commit_step(env, 'Step 11: Chat Conversations')

    # =================================================================
    # STEP 12: VALIDATION
    # =================================================================
    log('\n' + '=' * 60)
    log('VALIDATION REPORT')
    log('=' * 60)

    errors = []

    # Doctors
    for doc in Doctor.search([]):
        if doc.specialty_id and doc.cabinet_id and doc.user_id:
            log(f'  OK: Doctor {doc.name} ({doc.specialty_id.name}, {doc.cabinet_id.name})')
        else:
            errors.append(f'Doctor {doc.name} missing specialty/cabinet/user')

    # Patients
    for pat in Patient.search([]):
        if pat.user_id:
            log(f'  OK: Patient {pat.name} ({pat.gender}, {pat.blood_group})')
        else:
            errors.append(f'Patient {pat.name} missing user_id')

    # Care relationships
    rels = CareRel.search([('active', '=', True)])
    log(f'  OK: {len(rels)} active care relationships')
    for r in rels:
        log(f'    - {r.patient_id.name} <-> {r.doctor_id.name} ({r.relationship_type})')

    # Lab orgs
    for lab in LabOrg.search([]):
        staff = lab.user_ids
        log(f'  OK: Lab "{lab.name}" - {len(staff)} staff linked')
        if not staff:
            errors.append(f'Lab "{lab.name}" has no staff users linked')

    # Pharmacy orgs
    for pharm in PharmacyOrg.search([]):
        staff = pharm.user_ids
        log(f'  OK: Pharmacy "{pharm.name}" - {len(staff)} staff linked')
        if not staff:
            errors.append(f'Pharmacy "{pharm.name}" has no staff users linked')

    # Consultations
    consultations = Consultation.search([])
    log(f'  OK: {len(consultations)} consultations')

    # Medical records
    records = MedicalRecord.search([])
    log(f'  OK: {len(records)} medical records')

    # Lab requests
    lab_reqs = LabRequest.search([])
    for lr in lab_reqs:
        log(f'  OK: Lab request "{lr.analysis_type}" for {lr.patient_id.name} [{lr.status}]')
    lab_results = LabResult.search([])
    log(f'  OK: {len(lab_results)} lab results')

    # Prescriptions
    prescriptions = Prescription.search([])
    for p in prescriptions:
        log(f'  OK: Prescription "{p.medication}" for {p.patient_id.name} [{p.pharmacy_status}]')

    # Chat
    convs = ChatConversation.search([])
    log(f'  OK: {len(convs)} chat conversations')

    log('')
    if errors:
        log('ERRORS:')
        for e in errors:
            log(f'  FAIL: {e}')
        return False

    log('ALL VALIDATIONS PASSED!')
    log('')
    log('Summary:')
    log(f'  Doctors: {len(Doctor.search([]))}')
    log(f'  Patients: {len(Patient.search([]))}')
    log(f'  Care Relationships: {len(rels)}')
    log(f'  Consultations: {len(consultations)}')
    log(f'  Medical Records: {len(records)}')
    log(f'  Lab Requests: {len(lab_reqs)}')
    log(f'  Lab Results: {len(lab_results)}')
    log(f'  Prescriptions: {len(prescriptions)}')
    log(f'  Chat Conversations: {len(convs)}')
    return True


if __name__ == '__main__':
    print('Run inside Odoo shell:')
    print('  docker exec -it sanad_odoo odoo shell -d sanad_db -c /etc/odoo/odoo.conf')
    print('  >>> exec(open("/mnt/extra-addons/scripts/sanad_demo_data.py").read())')
    print('  >>> create_all(env)')
