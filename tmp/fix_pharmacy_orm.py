import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID

# Use the registry directly for a fully fresh environment
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

# Step 1: Write via ORM
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    org = env['sanad.pharmacy.org'].browse(1)
    user = env['res.users'].browse(7)
    print("Step 1 - Before write: org.user_ids.ids = %s" % org.user_ids.ids)
    org.write({'user_ids': [(4, user.id)]})
    cr.commit()
    print("Step 1 - After write + commit")

# Step 2: Read via completely fresh cursor
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    org = env['sanad.pharmacy.org'].browse(1)
    print("Step 2 - Fresh cursor: org.user_ids.ids = %s" % org.user_ids.ids)
    print("Step 2 - Fresh cursor: org.user_ids.logins = %s" % [u.login for u in org.user_ids])
    cr.commit()
