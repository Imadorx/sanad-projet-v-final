# Fix pharmacy user linkage
pharm_sanad = env['sanad.pharmacy.org'].search([('name', '=', 'Pharmacie SANAD')], limit=1)
pharm_alamal = env['sanad.pharmacy.org'].search([('name', '=', 'Pharmacie Al Amal')], limit=1)

# Find pharmacy users
pharmacy_test = env['res.users'].search([('login', '=', 'pharmacy.test@sanad.local')], limit=1)
alamal_user = env['res.users'].search([('login', '=', 'pharmacy.alamal@test.sanad')], limit=1)

print(f"Pharmacie SANAD: id={pharm_sanad.id} users_before={pharm_sanad.user_ids.mapped('login')}")
print(f"Pharmacie Al Amal: id={pharm_alamal.id} users_before={pharm_alamal.user_ids.mapped('login')}")
print(f"pharmacy.test user: id={pharmacy_test.id} login={pharmacy_test.login}")
print(f"pharmacy.alamal user: id={alamal_user.id} login={alamal_user.login}")

# Link pharmacy.test -> Pharmacie SANAD (Casablanca)
pharm_sanad.write({'user_ids': [(4, pharmacy_test.id)]})
print(f"Linked pharmacy.test to Pharmacie SANAD -> users now: {pharm_sanad.user_ids.mapped('login')}")

# Link pharmacy.alamal -> Pharmacie Al Amal (Rabat)
pharm_alamal.write({'user_ids': [(4, alamal_user.id)]})
print(f"Linked pharmacy.alamal to Pharmacie Al Amal -> users now: {pharm_alamal.user_ids.mapped('login')}")

env.cr.commit()
print("Pharmacy user linkage fixed!")
