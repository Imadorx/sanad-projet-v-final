# -*- coding: utf-8 -*-
{
    'name': 'SANAD Pharmacy',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Pharmacy prescription processing workflow',
    'description': """
SANAD Pharmacy
===============
Pharmacy workflow module (PRD 5.5 / 10.5).

sanad.prescription already exists in sanad_medical with a pharmacy_status
field (Received / Prepared / Completed) and a pharmacy_id assignment
field, plus a record rule scoping visibility to a pharmacy's own staff
(sanad.pharmacy.org.user_ids, added in sanad_medical). This module adds
the pharmacy-facing workflow actions and a dedicated, field-restricted
view so pharmacy staff interact only with what PRD 14.3 allows them to
see (medication/dosage/instructions - not full medical records).
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core', 'sanad_medical'],
    'data': [
        'security/sanad_pharmacy_record_rules.xml',
        'views/sanad_pharmacy_prescription_views.xml',
        'views/sanad_pharmacy_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
