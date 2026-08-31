# Check and set passwords for demo users
users = env['res.users'].search([('login', 'like', '%@test.sanad'), '|', ('login', 'like', '%@sanad.local'), ('login', '=', 'admin')])
for u in users:
    # Check if user has password
    env.cr.execute("SELECT login FROM res_users WHERE id = %s AND password IS NOT NULL", (u.id,))
    has_pw = env.cr.fetchone()
    print(f"  id={u.id} login={u.login} has_password={has_pw is not None}")

# Set password 'admin' for test users
test_logins = [
    'ahmed.benali@test.sanad',
    'pharmacy.test@sanad.local',
    'pharmacy.alamal@test.sanad',
    'sara.alaoui@test.sanad',
    'youssef.amrani@test.sanad',
    'lina.mansouri@test.sanad',
    'sara.bennani@test.sanad',
    'omar.tazi@test.sanad',
    'yasmine.amrani@test.sanad',
    'admin',
]
for login in test_logins:
    u = env['res.users'].search([('login', '=', login)], limit=1)
    if u:
        u.sudo().write({'password': 'admin'})
        print(f"  Set password for {login}")

env.cr.commit()
print("Done!")
