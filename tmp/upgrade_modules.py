import odoo
from odoo.tools import config

config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db'])

from odoo.modules.registry import Registry
from odoo import api, SUPERUSER_ID

# Use odoo.service.server to run the upgrade properly
import odoo.modules.module
import odoo.modules.graph

# Initialize the registry
registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Trigger upgrade via module state update
    modules_to_upgrade = ['sanad_core', 'sanad_ai', 'sanad_chat', 'sanad_laboratory', 'sanad_medical', 'sanad_patient', 'sanad_pharmacy']
    for mod_name in modules_to_upgrade:
        mod = env['ir.module.module'].search([('name', '=', mod_name)])
        if mod:
            mod.write({'state': 'to upgrade'})
            print(f'Set {mod_name} to to upgrade')
    cr.commit()

print('Module states updated. Running full update...')
