from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # List all users with roles
    users = env["res.users"].search([("login", "!=", "admin")])
    for u in users:
        roles = []
        if u.has_group("sanad_core.group_sanad_admin"):
            roles.append("admin")
        if u.has_group("sanad_core.group_sanad_doctor"):
            roles.append("doctor")
        if u.has_group("sanad_core.group_sanad_patient"):
            roles.append("patient")
        if u.has_group("sanad_core.group_sanad_laboratory"):
            roles.append("lab")
        if u.has_group("sanad_core.group_sanad_pharmacy"):
            roles.append("pharmacy")
        doctor_id = ""
        if u.has_group("sanad_core.group_sanad_doctor"):
            doc = env["sanad.doctor"].search([("user_id", "=", u.id)], limit=1)
            doctor_id = doc.id if doc else "NONE"
        pharmacy_id = ""
        if u.has_group("sanad_core.group_sanad_pharmacy"):
            po = env["sanad.pharmacy.org"].search([], limit=5)
            pharmacy_id = [(p.id, p.name) for p in po]
        print(f"  id={u.id} login={u.login} name={u.name} roles={roles} doctor_id={doctor_id} pharmacy_orgs={pharmacy_id}")
    
    # Set passwords for known users
    logins_to_set = [
        "ahmed.benali@test.sanad",
        "sara.alaoui@test.sanad",
        "pharmacy.test@sanad.local",
        "pharmacy.alamal@test.sanad",
        "patient.test@sanad.local",
        "lab.test@sanad.local",
        "doctor.demo@sanad-health.example.com",
        "patient.demo@sanad-health.example.com",
    ]
    for login in logins_to_set:
        user = env["res.users"].search([("login", "=", login)], limit=1)
        if user:
            user.sudo().write({"password": "demo1234"})
            print(f"  Set password for {login}")
        else:
            print(f"  User {login} not found")
    
    # Also list pharmacy orgs
    print("\n--- Pharmacy Orgs ---")
    orgs = env["sanad.pharmacy.org"].search([("active", "=", True)])
    for o in orgs:
        users_list = [u.login for u in o.user_ids] if hasattr(o, 'user_ids') else "N/A"
        print(f"  id={o.id} name={o.name} users={users_list}")
    
    # List doctors
    print("\n--- Doctors ---")
    docs = env["sanad.doctor"].search([])
    for d in docs:
        print(f"  id={d.id} name={d.name} user_id={d.user_id.id} user_login={d.user_id.login}")
    
    cr.commit()
