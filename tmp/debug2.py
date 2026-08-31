from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Pharmacy org user_ids
    print("=== Pharmacy Org user_ids ===")
    orgs = env['sanad.pharmacy.org'].search([])
    for o in orgs:
        uid = o.user_ids.ids if hasattr(o, 'user_ids') and o.user_ids else 'EMPTY'
        print("  id=%d name=%s user_ids=%s" % (o.id, o.name, uid))
    
    # Record rules on sanad.prescription
    print("\n=== Record Rules on sanad.prescription ===")
    rules = env['ir.rule'].search([('model_id.model', '=', 'sanad.prescription')])
    for r in rules:
        grps = [g.name for g in r.groups] if r.groups else ['(global)']
        print("  id=%d name=%s groups=%s" % (r.id, r.name, grps))
        print("    domain=%s" % (r.domain_force[:300] if r.domain_force else 'None'))
    
    # Check author_id mapping
    print("\n=== User ID mapping ===")
    u5 = env['res.users'].browse(5)
    u6 = env['res.users'].browse(6)
    print("  user 5: %s (login=%s)" % (u5.name, u5.login))
    print("  user 6: %s (login=%s)" % (u6.name, u6.login))
    
    cr.commit()
