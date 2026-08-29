# -*- coding: utf-8 -*-
{
    'name': 'SANAD Medical',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Medical records, consultations and prescriptions',
    'description': """
SANAD Medical
=============
Core clinical workflow module.

Provides:
- sanad.medical.record: one summary medical record per patient, the
  parent container for consultations, prescriptions and (from Phase 4)
  lab results
- sanad.consultation: individual doctor visits with reason, symptoms,
  observations, clinical notes, report and attachments
- sanad.prescription: medication prescriptions issued during or after
  a consultation
- Access strictly scoped through sanad.patient.doctor.rel: a doctor can
  only create/view consultations and prescriptions for patients they
  have an active care relationship with
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core', 'sanad_patient'],
    'data': [
        'security/ir.model.access.csv',
        'security/sanad_medical_record_rules.xml',
        # Order matters: sanad_prescription_views.xml defines
        # action_sanad_prescription, which BOTH sanad_consultation_views.xml
        # (prescriptions stat-button) and sanad_medical_record_views.xml
        # (prescriptions stat-button) reference. sanad_consultation_views.xml
        # defines action_sanad_consultation, which sanad_medical_record_views.xml
        # also references. Load prescriptions -> consultations -> medical
        # record so every action referenced by an earlier file is already
        # defined by the time it's needed.
        'views/sanad_prescription_views.xml',
        'views/sanad_consultation_views.xml',
        'views/sanad_medical_record_views.xml',
        'views/sanad_medical_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
