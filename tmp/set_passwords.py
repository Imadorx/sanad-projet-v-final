# Set all demo user passwords to 'admin'
login_list = [
    'ahmed.benali@test.sanad',
    'pharmacy.test@sanad.local',
    'pharmacy.alamal@test.sanad',
    'sara.alaoui@test.sanad',
    'youssef.amrani@test.sanad',
    'lina.mansouri@test.sanad',
    'sara.bennani@test.sanad',
    'omar.tazi@test.sanad',
    'yasmine.amrani@test.sanad',
    'lab.biomed@test.sanad',
]
for login in login_list:
    u = env['res.users'].search([('login', '=', login)], limit=1)
    if u:
        u._set_password('admin')
        print(f"  Set password for {login}")
env.cr.commit()
print("All passwords set to 'admin'!")
