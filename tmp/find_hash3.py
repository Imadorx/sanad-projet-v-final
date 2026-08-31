# Find Odoo 19 password hashing
# Use res.users._set_password through internal mechanism
u = env['res.users'].search([('login', '=', 'admin')], limit=1)
# Check the crypt context
from odoo.addons.base.models.res_users import check_session
print(type(u))
print(dir(u))
# Just try to verify a known password
print(u._check_password('admin'))
