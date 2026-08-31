import odoo
from odoo.tools import config
config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check actual column names in M2M tables
    for table in ['res_users_sanad_pharmacy_org_rel', 'res_users_sanad_laboratory_org_rel']:
        cr.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' 
            ORDER BY ordinal_position
        """)
        rows = cr.fetchall()
        print(f'{table}: {rows}')
        cr.execute(f"SELECT * FROM {table}")
        print(f'  Data: {cr.fetchall()}')
