# Check login details for users
users = env['res.users'].sudo().search([])
for u in users:
    if 'test.sanad' in u.login or 'sanad.local' in u.login or u.login == 'admin':
        env.cr.execute("SELECT COALESCE(password, 'NULL') FROM res_users WHERE id = %s", (u.id,))
        pw = env.cr.fetchone()
        print(f"  id={u.id} login={u.login} password_hash={'set' if pw[0] != 'NULL' else 'NULL'}")
