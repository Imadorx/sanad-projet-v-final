from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules = env["ir.module.module"].search([("name","like","sanad%")])
    for m in modules:
        print(f"{m.name}: state={m.state}, version={m.installed_version}")
