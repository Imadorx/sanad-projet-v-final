import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

with registry.cursor() as cr:
    # Clean up stale rows from earlier debugging
    cr.execute("DELETE FROM res_users_sanad_pharmacy_org_rel")
    # Insert only the correct link: Pharmacy Test (org 1) <-> pharmacy.test@sanad.local (user 7)
    cr.execute("INSERT INTO res_users_sanad_pharmacy_org_rel (sanad_pharmacy_org_id, res_users_id) VALUES (1, 7)")
    cr.commit()
    
    cr.execute("SELECT * FROM res_users_sanad_pharmacy_org_rel")
    print("Clean table:", cr.fetchall())
