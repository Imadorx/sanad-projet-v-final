from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Check the actual table and column name for the Many2many
    cr.execute("SELECT relname FROM pg_class WHERE relname LIKE '%pharmacy%user%' OR relname LIKE '%user%pharmacy%'")
    tables = cr.fetchall()
    print("M2M tables:", tables)

    # Check the field info
    field = env['sanad.pharmacy.org']._fields.get('user_ids')
    if field:
        print("Field type:", type(field).__name__)
        print("Field relation:", field.relation)
        print("Field column1:", field.column1)
        print("Field column2:", field.column2)
    else:
        print("user_ids field not found on sanad.pharmacy.org")

    # Direct SQL approach
    if field:
        rel_table = field.relation
        col1 = field.column1
        col2 = field.column2
        # Insert the link
        cr.execute("INSERT INTO %s (%s, %s) VALUES (%%s, %%s) ON CONFLICT DO NOTHING" % (rel_table, col1, col2), (1, 7))
        cr.commit()
        print("SQL INSERT done: (%s, %s) = (1, 7)" % (col1, col2))

        # Verify
        cr.execute("SELECT * FROM %s WHERE %s = %%s" % (rel_table, col1), (1,))
        rows = cr.fetchall()
        print("Verification rows:", rows)

        # Also read back via ORM
        env.invalidate_all()
        org = env['sanad.pharmacy.org'].browse(1)
        print("ORM readback user_ids:", org.user_ids.ids)
