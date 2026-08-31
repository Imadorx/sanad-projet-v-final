import odoo
from odoo.tools import config
config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([('name', '=', 'sanad_chat')], limit=1)
    if module:
        module.button_immediate_install()
    cr.commit()
    print('[OK] sanad_chat reinstalled')
