import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Verify field domain is now empty
    field = env['sanad.pharmacy.org']._fields['user_ids']
    print("Field domain:", field.domain)
    
    # Verify ORM reads user_ids correctly
    org = env['sanad.pharmacy.org'].browse(1)
    print("Pharmacy Test (id=1) user_ids:", org.user_ids.ids)
    print("Pharmacy Test (id=1) user_ids logins:", [u.login for u in org.user_ids])
    
    # Verify all orgs
    orgs = env['sanad.pharmacy.org'].search([('active', '=', True)], order='name')
    for o in orgs:
        print("  org id=%d name='%s' user_ids=%s" % (o.id, o.name, o.user_ids.ids))
    
    # Verify the record rule would now match
    # pharmacy user id=7 should see prescriptions where pharmacy_id.user_ids contains 7
    user = env['res.users'].browse(7)
    rx = env['sanad.prescription'].browse(28)
    print("\nRX#28 pharmacy_id:", rx.pharmacy_id.id)
    print("User 7 in pharmacy_id.user_ids:", user.id in rx.pharmacy_id.user_ids.ids if rx.pharmacy_id else "N/A")
    
    cr.commit()
