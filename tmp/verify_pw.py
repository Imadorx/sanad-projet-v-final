# Verify the admin password works by using session authenticate
# This tests if our hash format is compatible with Odoo's verification
result = env['res.users'].sudo()._check_credentials({'login': 'admin', 'password': 'admin'})
print(f"Admin login check: {result}")
