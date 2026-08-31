# Set all demo user passwords to 'admin' using passlib
from passlib.context import CryptContext
pwd_ctx = CryptContext(schemes=['pbkdf2_sha512'], deprecated='auto')
hashed = pwd_ctx.hash('admin')
print(f"Generated hash: {hashed[:40]}...")

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
    'lab.test@sanad.local',
    'patient.test@sanad.local',
    'admin',
]

for login in login_list:
    env.cr.execute("UPDATE res_users SET password = %s WHERE login = %s", (hashed, login))
    print(f"  Updated {login} ({env.cr.rowcount} rows)")

env.cr.commit()
print("All passwords updated!")
