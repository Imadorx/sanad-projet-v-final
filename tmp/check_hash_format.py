# Use Odoo's internal mechanism to set password
# In Odoo 19, password hashing is done via res.users._set_password
# Let's find the actual method
User = env['res.users'].sudo()

# Use the login endpoint mechanism instead - just test with HTTP
# First check what password hashing Odoo 19 uses by looking at the res_users table
env.cr.execute("SELECT password FROM res_users WHERE login = 'admin' LIMIT 1")
row = env.cr.fetchone()
if row and row[0]:
    print(f"Admin password hash format: {row[0][:50]}...")
    # Check if it's a known format
    if row[0].startswith('$pbkdf2'):
        print("Format: pbkdf2_sha256")
    elif row[0].startswith('$1$'):
        print("Format: md5crypt")
    elif '$' in row[0]:
        print("Format: likely passlib")
    else:
        print("Format: unknown")
else:
    print("No password found for admin")
