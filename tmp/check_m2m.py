# Check the Many2many relation table
env.cr.execute("SELECT id, name FROM sanad_pharmacy_org")
pharmacies = env.cr.fetchall()
print("Pharmacy orgs:", pharmacies)

# Find the m2m relation table name - it's usually auto-named
env.cr.execute("""
    SELECT conname, contype, conrelid::regclass, confrelid::regclass, 
           pg_get_constraintdef(oid)
    FROM pg_constraint 
    WHERE conrelid = 'sanad_pharmacy_org'::regclass AND contype = 'r'
""")
print("\nFK constraints on sanad_pharmacy_org:")
for row in env.cr.fetchall():
    print(f"  {row}")

# Check if there's a relation table
env.cr.execute("""
    SELECT c.relname 
    FROM pg_class c 
    WHERE c.relname LIKE '%pharmacy%' AND c.relkind = 'r'
""")
print("\nTables with 'pharmacy':", [r[0] for r in env.cr.fetchall()])

# Try inserting directly via SQL
env.cr.execute("SELECT id FROM res_users WHERE login = 'pharmacy.test@sanad.local'")
user_row = env.cr.fetchone()
env.cr.execute("SELECT id FROM sanad_pharmacy_org WHERE name = 'Pharmacie SANAD'")
pharm_row = env.cr.fetchone()
print(f"\nuser_id={user_row}, pharmacy_id={pharm_row}")

if user_row and pharm_row:
    # Find the m2m table
    env.cr.execute("""
        SELECT c.relname FROM pg_class c
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'sanad_pharmacy_org_id'
        WHERE c.relname LIKE '%sanad_pharmacy_org%' AND c.relkind = 'r'
    """)
    tables = env.cr.fetchall()
    print(f"M2M tables: {[t[0] for t in tables]}")
    
    for t in tables:
        tname = t[0]
        env.cr.execute(f'SELECT * FROM "{tname}"')
        rows = env.cr.fetchall()
        print(f"  {tname}: {rows}")
