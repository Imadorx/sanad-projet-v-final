import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check the field's domain
    field = env['sanad.pharmacy.org']._fields['user_ids']
    print("user_ids domain:", field.domain)
    
    # Check how the ORM builds the SQL for reading user_ids
    org = env['sanad.pharmacy.org'].browse(1)
    
    # Force read with sudo and clear cache
    env.cache.invalidate([
        (env['sanad.pharmacy.org'], 1, 'user_ids'),
    ])
    
    # Try reading with explicit active_test=False
    user_ids = org.sudo().user_ids
    print("sudo user_ids:", user_ids.ids)
    print("sudo user_ids logins:", [u.login for u in user_ids])
    
    # Try searching users that match the domain
    users = env['res.users'].search([('group_ids', 'in', [])])
    print("Users matching domain [('group_ids', 'in', [])]:", users.ids, users.mapped('login'))
    
    # Try with empty domain
    users2 = env['res.users'].search([])
    print("All users count:", len(users2))
    
    # Try to read the m2m via _search
    cr.execute("SELECT res_users_id FROM res_users_sanad_pharmacy_org_rel WHERE sanad_pharmacy_org_id = 1")
    print("Raw SQL user IDs linked to org 1:", cr.fetchall())
