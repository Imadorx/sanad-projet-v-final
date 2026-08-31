# Fix pharmacy user linkage - with explicit commit
pharm_sanad = env['sanad.pharmacy.org'].sudo().search([('name', '=', 'Pharmacie SANAD')], limit=1)
pharm_alamal = env['sanad.pharmacy.org'].sudo().search([('name', '=', 'Pharmacie Al Amal')], limit=1)

pharmacy_test = env['res.users'].sudo().search([('login', '=', 'pharmacy.test@sanad.local')], limit=1)
alamal_user = env['res.users'].sudo().search([('login', '=', 'pharmacy.alamal@test.sanad')], limit=1)

print(f"Before: SANAD users={pharm_sanad.user_ids.mapped('login')}")
print(f"Before: Al Amal users={pharm_alamal.user_ids.mapped('login')}")

# Link
pharm_sanad.sudo().write({'user_ids': [(4, pharmacy_test.id)]})
pharm_alamal.sudo().write({'user_ids': [(4, alamal_user.id)]})

env.cr.commit()
print(f"After: SANAD users={pharm_sanad.user_ids.mapped('login')}")
print(f"After: Al Amal users={pharm_alamal.user_ids.mapped('login')}")
print("Committed!")
