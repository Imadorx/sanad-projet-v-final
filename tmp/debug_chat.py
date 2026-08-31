from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check raw body of message 400 (the HTML test message)
    msg = env['mail.message'].browse(400)
    if msg.exists():
        print("=== Raw mail.message id=400 ===")
        print("body repr:", repr(msg.body)[:500])
        print("body plain:", msg.body[:500])
    else:
        print("Message 400 not found in mail.message")
    
    # Check the chat message record if it exists
    chat_msgs = env['sanad.chat.message'].search([('message_id', '=', 400)])
    if chat_msgs:
        print("\n=== sanad.chat.message ===")
        print("body:", chat_msgs[0].body[:500])
    else:
        # Try by conversation
        chat_msgs = env['sanad.chat.message'].search([], order='id desc', limit=5)
        print("\n=== Last 5 sanad.chat.message records ===")
        for m in chat_msgs:
            print(f"  id={m.id} message_id={m.message_id.id if m.message_id else 'None'} body={repr(m.body)[:120]}")
    
    # Check the pharmacy org user_ids
    print("\n=== Pharmacy Org user_ids ===")
    orgs = env['sanad.pharmacy.org'].search([])
    for o in orgs:
        print(f"  id={o.id} name={o.name} user_ids={o.user_ids.ids if hasattr(o, 'user_ids') and o.user_ids else 'EMPTY'}")
    
    # Check record rules on sanad.prescription
    print("\n=== Record Rules on sanad.prescription ===")
    rules = env['ir.rule'].search([('model_id.model', '=', 'sanad.prescription')])
    for r in rules:
        print(f"  id={r.id} name={r.name} groups={[g.name for g in r.groups]} domain_force={r.domain_force[:200] if r.domain_force else 'None'}")
    
    cr.commit()
