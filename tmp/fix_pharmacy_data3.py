from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check raw SQL first
    cr.execute("SELECT * FROM res_users_sanad_pharmacy_org_rel WHERE sanad_pharmacy_org_id = 1")
    rows = cr.fetchall()
    print("Raw SQL rows:", rows)

    # Force full invalidation
    env.clear()
    env.reset()

    org = env['sanad.pharmacy.org'].browse(1)
    print("After reset, user_ids:", org.user_ids.ids)
    print("After reset, user_ids logins:", [u.login for u in org.user_ids])

    # Also check from the user side
    user = env['res.users'].browse(7)
    print("User 7 login:", user.login)

    cr.commit()
