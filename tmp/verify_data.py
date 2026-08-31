# Verify data is consistent
print("=== Pharmacies ===")
pharmacies = env['sanad.pharmacy.org'].search([])
for ph in pharmacies:
    user_logins = [u.login for u in ph.user_ids]
    print(f"  {ph.name} -> users: {user_logins}")

print("\n=== Prescriptions (all) ===")
prescriptions = env['sanad.prescription'].sudo().search([])
for p in prescriptions:
    ph_name = p.pharmacy_id.name if p.pharmacy_id else 'NONE'
    print(f"  id={p.id} patient={p.patient_id.name} pharmacy={ph_name} status={p.pharmacy_status}")

# Simulate what the record rule does for pharmacy.test user
print("\n=== Record rule check for pharmacy.test@sanad.local ===")
pharmacy_user = env['res.users'].sudo().search([('login', '=', 'pharmacy.test@sanad.local')], limit=1)
PharmacyEnv = env(user=pharmacy_user)
visible = PharmacyEnv['sanad.prescription'].search([])
print(f"  pharmacy.test can see {len(visible)} prescriptions:")
for p in visible:
    print(f"    id={p.id} medication={p.medication} status={p.pharmacy_status}")
