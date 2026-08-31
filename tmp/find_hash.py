# Find how Odoo hashes passwords
from odoo.service import security
print(dir(security))
print()
# Try the common method
try:
    h = security.hash_password('admin')
    print(f"hash_password('admin') = {h[:30]}...")
except Exception as e:
    print(f"hash_password error: {e}")
