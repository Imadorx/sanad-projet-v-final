#!/usr/bin/env python3
"""Wrapper script to run demo data creation in Odoo shell."""
import odoo
from odoo.tools import config

# Parse config
config.parse_config(['--config=/etc/odoo/odoo.conf', '-d', 'sanad_db'])

# Initialize Odoo
odoo.modules.module.load_manifest = odoo.modules.module.load_manifest
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

registry = Registry('sanad_db')
registry.setup_signaling()

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Import and run the demo data script
    exec(open('/mnt/extra-addons/scripts/sanad_demo_data.py').read())
    create_all(env)
    
    # Commit the transaction
    cr.commit()
    print('\n[SUCCESS] Demo data committed to database.')
