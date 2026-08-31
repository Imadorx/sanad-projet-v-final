import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # 1) Confirm raw SQL shows the link
    cr.execute("SELECT * FROM res_users_sanad_pharmacy_org_rel WHERE sanad_pharmacy_org_id = 1")
    print("Raw SQL rows for org 1:", cr.fetchall())

    # 2) Check the field domain
    field = env['sanad.pharmacy.org']._fields['user_ids']
    print("Field domain:", field.domain)

    # 3) Direct ORM read - uses sudo to bypass record rules
    org = env['sanad.pharmacy.org'].browse(1)
    # Read _prefetch_ids to force the field
    org._read(['user_ids'])
    print("After _read: user_ids =", org.user_ids.ids)

    # 4) Check what SQL the ORM generates for the m2m read
    # Use with_context to disable active_test and domain
    org2 = env['sanad.pharmacy.org'].with_context(prefetch_fields=False).browse(1)
    # Just do a direct attribute access
    ids = org2.user_ids.ids
    print("Direct attr: user_ids =", ids)

    # 5) Search for users matching the domain
    matching_users = env['res.users'].search(field.domain)
    print("Users matching domain:", matching_users.ids)

    cr.commit()
