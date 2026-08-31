from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Link pharmacy.test@sanad.local (user id=7) to Pharmacy Test (org id=1)
    org = env['sanad.pharmacy.org'].browse(1)
    user = env['res.users'].browse(7)
    print("Before: org=%s user_ids=%s" % (org.name, org.user_ids.ids))
    org.write({'user_ids': [(4, user.id)]})
    org.invalidate_recordset(['user_ids'])
    print("After:  org=%s user_ids=%s" % (org.name, org.user_ids.ids))

    # Verify
    org2 = env['sanad.pharmacy.org'].browse(1)
    print("Verify: user_ids=%s contains user 7=%s" % (org2.user_ids.ids, user.id in org2.user_ids.ids))

    cr.commit()
    print("DONE")
