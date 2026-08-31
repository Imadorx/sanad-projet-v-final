import json

# 1. Check demo data users
print("=== Users ===")
users = env['res.users'].search([])
for u in users:
    roles = []
    if u.has_group('sanad_core.group_sanad_doctor'):
        roles.append('doctor')
    if u.has_group('sanad_core.group_sanad_patient'):
        roles.append('patient')
    if u.has_group('sanad_core.group_sanad_pharmacy'):
        roles.append('pharmacy')
    if u.has_group('sanad_core.group_sanad_admin'):
        roles.append('admin')
    print(f"  id={u.id} login={u.login} name={u.name} roles={','.join(roles) if roles else 'none'}")

# 2. Check pharmacies
print("\n=== Pharmacies ===")
pharmacies = env['sanad.pharmacy.org'].search([])
for ph in pharmacies:
    user_logins = [u.login for u in ph.user_ids]
    print(f"  id={ph.id} name={ph.name} address={ph.address} users={user_logins}")

# 3. Check prescriptions
print("\n=== Prescriptions ===")
prescriptions = env['sanad.prescription'].search([])
for p in prescriptions:
    ph_name = p.pharmacy_id.name if p.pharmacy_id else 'NONE'
    print(f"  id={p.id} patient={p.patient_id.name} doctor={p.doctor_id.name} pharmacy={ph_name} status={p.pharmacy_status}")
