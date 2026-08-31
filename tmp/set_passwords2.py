# Set passwords using SQL directly
import hashlib, os

def hash_password(password):
    """Hash password using Odoo's method"""
    from odoo.tools.misc import str2bool
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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

try:
    hashed = hash_password('admin')
except:
    # fallback: use odoo's own method
    from odoo import service
    hashed = service.security.pycryptodome_hash('admin')

print(f"Using hash method, hash starts with: {hashed[:10]}...")

for login in login_list:
    env.cr.execute("UPDATE res_users SET password = %s WHERE login = %s", (hashed, login))
    if env.cr.rowcount > 0:
        print(f"  Updated {login}")
    else:
        print(f"  NOT FOUND: {login}")

env.cr.commit()
print("All passwords updated!")
