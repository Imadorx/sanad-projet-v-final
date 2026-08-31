import odoo
from odoo.tools import config
config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    print('=== FINAL DATA VERIFICATION ===')
    
    # Doctors
    doctors = env['sanad.doctor'].search([])
    print(f'\nDoctors: {len(doctors)}')
    for d in doctors:
        print(f'  {d.name} ({d.specialty_id.name}, {d.cabinet_id.name}) user={d.user_id.login}')
    
    # Patients
    patients = env['sanad.patient'].search([])
    print(f'\nPatients: {len(patients)}')
    for p in patients:
        print(f'  {p.name} ({p.gender}, {p.blood_group}) user={p.user_id.login}')
    
    # Care relationships
    rels = env['sanad.patient.doctor.rel'].search([('active', '=', True)])
    print(f'\nCare Relationships: {len(rels)}')
    for r in rels:
        print(f'  {r.patient_id.name} <-> {r.doctor_id.name} ({r.relationship_type})')
    
    # Lab orgs + staff
    print('\nLab Orgs:')
    for lab in env['sanad.laboratory.org'].search([]):
        cr.execute('SELECT res_users_id FROM res_users_sanad_laboratory_org_rel WHERE sanad_laboratory_org_id = %s', (lab.id,))
        user_ids = [r[0] for r in cr.fetchall()]
        users = env['res.users'].browse(user_ids)
        print(f'  {lab.name}: staff={users.mapped("login")}')
    
    # Pharmacy orgs + staff
    print('\nPharmacy Orgs:')
    for ph in env['sanad.pharmacy.org'].search([]):
        cr.execute('SELECT res_users_id FROM res_users_sanad_pharmacy_org_rel WHERE sanad_pharmacy_org_id = %s', (ph.id,))
        user_ids = [r[0] for r in cr.fetchall()]
        users = env['res.users'].browse(user_ids)
        print(f'  {ph.name}: staff={users.mapped("login")}')
    
    # Consultations
    consults = env['sanad.consultation'].search([])
    print(f'\nConsultations: {len(consults)}')
    for c in consults:
        print(f'  {c.reason} - {c.patient_id.name} with {c.doctor_id.name}')
    
    # Lab requests
    labs = env['sanad.lab.request'].search([])
    print(f'\nLab Requests: {len(labs)}')
    for l in labs:
        print(f'  {l.analysis_type} - {l.patient_id.name} [{l.status}] -> {l.laboratory_id.name}')
    
    # Lab results
    results = env['sanad.lab.result'].search([])
    print(f'\nLab Results: {len(results)}')
    
    # Prescriptions
    rxs = env['sanad.prescription'].search([])
    print(f'\nPrescriptions: {len(rxs)}')
    for r in rxs:
        print(f'  {r.medication} ({r.dosage}) - {r.patient_id.name} [{r.pharmacy_status}]')
    
    # Chat conversations
    chats = env['sanad.chat.conversation'].search([])
    print(f'\nChat Conversations: {len(chats)}')
    for c in chats:
        participants = c.participant_ids.mapped('name')
        print(f'  {c.conversation_type}: {" <-> ".join(participants)}')
    
    # Users
    users = env['res.users'].search([('login', 'like', '%.test.sanad'), ('login', '!=', 'admin')])
    print(f'\nDemo Users: {len(users)}')
    for u in users:
        groups = u.groups_id.mapped('name') if hasattr(u, 'groups_id') else u.group_ids.mapped('name')
        print(f'  {u.login} groups={groups}')
