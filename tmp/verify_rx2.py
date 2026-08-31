from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry
registry = Registry("sanad_db")
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rx_id in [28, 29]:
        p = env["sanad.prescription"].browse(rx_id)
        if p.exists():
            phid = p.pharmacy_id.id if p.pharmacy_id else "None"
            print("  id=%d medication=%s doctor_id=%s pharmacy_id=%s patient_id=%s status=%s" % (p.id, p.medication, p.doctor_id.id, phid, p.patient_id.id, p.pharmacy_status))
        else:
            print("  id=%d DOES NOT EXIST" % rx_id)
    cr.commit()
