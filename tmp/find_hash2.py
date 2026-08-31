# Find Odoo 19 password hashing
from odoo.tools import password as pwd_module
print(dir(pwd_module))
print()
h = pwd_module.hash_password('admin')
print(f"hash_password('admin') = {h[:30]}...")
