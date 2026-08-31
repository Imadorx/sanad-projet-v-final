import odoo
from odoo.tools import config
config.parse_config(['-c', '/etc/odoo/odoo.conf', '-d', 'sanad_db', '--no-http'])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry('sanad_db')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check the actual field definition
    field = env['sanad.pharmacy.org']._fields.get('user_ids')
    print("Field relation table:", field.relation)
    print("Field column1:", field.column1)
    print("Field column2:", field.column2)
    
    # Check raw SQL of the table structure
    cr.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '%s' ORDER BY ordinal_position" % field.relation)
    cols = cr.fetchall()
    print("Table columns:", cols)
    
    # Check current data
    cr.execute("SELECT * FROM %s" % field.relation)
    rows = cr.fetchall()
    print("Current rows:", rows)
    
    # Try to insert with explicit SQL and verify ORM reads it
    # First delete any existing rows for org 1
    cr.execute("DELETE FROM %s WHERE %s = 1" % (field.relation, field.column1))
    cr.execute("INSERT INTO %s (%s, %s) VALUES (1, 7)" % (field.relation, field.column1, field.column2))
    cr.commit()
    print("Inserted (1, 7) via SQL")
    
    # Verify raw
    cr.execute("SELECT * FROM %s WHERE %s = 1" % (field.relation, field.column1))
    rows = cr.fetchall()
    print("After insert, rows:", rows)

# Now in a completely new process...
print("\n--- NEW PROCESS ---")

from odoo.modules.registry import Registry
registry2 = Registry('sanad_db')
with registry2.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    org = env['sanad.pharmacy.org'].browse(1)
    print("ORM user_ids:", org.user_ids.ids)
    
    # Try forcing read
    cr.execute("SELECT res_users_id FROM res_users_sanad_pharmacy_org_rel WHERE sanad_pharmacy_org_id = 1")
    raw = cr.fetchall()
    print("Raw SQL res_users_id:", raw)
