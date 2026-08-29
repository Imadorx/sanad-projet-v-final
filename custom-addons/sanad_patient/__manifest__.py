# -*- coding: utf-8 -*-
{
    'name': 'SANAD Patient',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Patient management and care relationships',
    'description': """
SANAD Patient
=============
Patient management module for the SANAD Healthcare Platform.

Provides:
- sanad.patient: patient medical profile, linked to res.partner/res.users
  (identity remains sourced from Odoo standard models; this model holds
  only healthcare-domain fields: blood group, allergies, chronic
  conditions, emergency contact, medical notes)
- sanad.patient.doctor.rel: the patient-doctor care relationship model
  that underpins RBAC across sanad_medical, sanad_laboratory and
  sanad_pharmacy (a doctor may only access patients they have an active
  care relationship with)
- Record rules enforcing patient self-access and doctor-scoped access
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core'],
    'data': [
        'security/sanad_patient_security.xml',
        'security/ir.model.access.csv',
        'security/sanad_patient_record_rules.xml',
        'views/sanad_patient_views.xml',
        'views/sanad_patient_doctor_rel_views.xml',
        'views/sanad_patient_menus.xml',
    ],
    'demo': ['data/sanad_patient_demo.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
