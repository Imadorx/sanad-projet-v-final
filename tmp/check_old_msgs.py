from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check which messages have double-encoded entities (old code artifacts)
    # vs single-encoded (Odoo's normal behavior)
    msgs = env['mail.message'].search([], order='id desc', limit=15)
    for m in msgs:
        raw = str(m.body)
        has_double = '&amp;' in raw and ('&lt;' in raw or '&gt;' in raw)
        print("id=%d double_encoded=%s raw=%s" % (m.id, has_double, raw[:120]))
    
    cr.commit()
