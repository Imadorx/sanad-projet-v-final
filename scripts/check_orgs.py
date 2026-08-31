import odoo
from odoo.tools import config
config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    lab_orgs = env['sanad.laboratory.org'].search([])
    for o in lab_orgs:
        print(f'Lab org: {o.name} (id={o.id}) user_ids={o.user_ids.mapped("login")}')
    pharma_orgs = env['sanad.pharmacy.org'].search([])
    for o in pharma_orgs:
        print(f'Pharmacy org: {o.name} (id={o.id}) user_ids={o.user_ids.mapped("login")}')
    # Check pharmacy test user
    u = env['res.users'].search([('login', '=', 'pharmacy.test@sanad.local')])
    if u:
        print(f'pharmacy.test user: id={u.id} groups={u.groups_id.mapped("name")}')
    else:
        print('pharmacy.test user NOT FOUND')
    # Check lab test user
    u2 = env['res.users'].search([('login', '=', 'lab.test@sanad.local')])
    if u2:
        print(f'lab.test user: id={u2.id} groups={u2.groups_id.mapped("name")}')
    else:
        print('lab.test user NOT FOUND')
