from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check the last few messages
    msgs = env['mail.message'].search([], order='id desc', limit=8)
    for m in msgs:
        print("id=%d body=%r" % (m.id, m.body[:200] if m.body else ''))
    
    cr.commit()
