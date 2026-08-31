import odoo
from odoo.tools import config
config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check what M2M relation table is used
    pharma_field = env['sanad.pharmacy.org']._fields.get('user_ids')
    print(f'Pharmacy user_ids type: {type(pharma_field).__name__}')
    print(f'Pharmacy user_ids relation: {pharma_field.relation if hasattr(pharma_field, "relation") else "N/A"}')
    
    lab_field = env['sanad.laboratory.org']._fields.get('user_ids')
    print(f'Lab user_ids type: {type(lab_field).__name__}')
    print(f'Lab user_ids relation: {lab_field.relation if hasattr(lab_field, "relation") else "N/A"}')
    
    # Direct SQL check
    cr.execute("SELECT conname FROM pg_constraint WHERE conrelid = 'sanad_pharmacy_org'::regclass AND contype = 'f'")
    print(f'Pharmacy FK constraints: {cr.fetchall()}')
    cr.execute("SELECT conname FROM pg_constraint WHERE conrelid = 'sanad_laboratory_org'::regclass AND contype = 'f'")
    print(f'Lab FK constraints: {cr.fetchall()}')
    
    # Check M2M tables directly
    cr.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%sanad%' AND table_type = 'BASE TABLE'")
    print(f'SANAD tables: {cr.fetchall()}')
    
    # Check the pharmacy org test user directly
    pharma = env['sanad.pharmacy.org'].search([('name', '=', 'Pharmacie SANAD')], limit=1)
    if pharma:
        print(f'Pharmacie SANAD id={pharma.id} user_ids={pharma.user_ids.ids}')
        # Try direct SQL
        cr.execute('SELECT * FROM sanad_pharmacy_org_res_users_rel WHERE sanad_pharmacy_org_id = %s', (pharma.id,))
        print(f'Direct SQL pharmacy rel: {cr.fetchall()}')
    
    # Check test pharmacy
    test_pharma = env['sanad.pharmacy.org'].search([('name', '=', 'Pharmacy Test')], limit=1)
    if test_pharma:
        print(f'Pharmacy Test id={test_pharma.id} user_ids={test_pharma.user_ids.ids}')
