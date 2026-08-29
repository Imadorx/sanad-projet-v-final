# -*- coding: utf-8 -*-
{
    'name': 'SANAD Core',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Core module: identity, roles, '
                'organizations and security foundation',
    'description': """
SANAD Core
==========
Foundation module for the SANAD Healthcare Platform.

This module provides:
- Organizational entities: Medical Cabinets, Laboratories, Pharmacies
- Doctor professional profile (linked to res.partner / res.users)
- Medical specialty catalog
- SANAD role-based security groups (Admin, Doctor, Patient, Laboratory,
  Pharmacy) with multi-role support
- Base record rules and access rights
- AI interaction audit log (sanad.ai.log)

All identity data (name, phone, email, address) is sourced from Odoo's
standard res.partner / res.users models. Custom SANAD models only carry
healthcare-domain-specific fields and never duplicate identity data.

This module does not manage patient medical data - see sanad_patient,
sanad_medical, sanad_laboratory, sanad_pharmacy, sanad_chat and sanad_ai
for domain-specific functionality built on top of this foundation.
    """,
    'author': 'SANAD Development Team',
    'website': 'https://sanad-health.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'web',
    ],
    'data': [
        # Security must load before views/menus reference groups
        'security/sanad_security_groups.xml',
        'security/ir.model.access.csv',
        'security/sanad_record_rules.xml',
        # Views - sanad_doctor_views.xml MUST load before
        # medical_cabinet_views.xml, which references action_sanad_doctor
        # (defined in sanad_doctor_views.xml) in a stat-button. This
        # ordering bug caused: ValueError: External ID not found in the
        # system: sanad_core.action_sanad_doctor - fixed by reordering.
        'views/sanad_medical_specialty_views.xml',
        'views/sanad_doctor_views.xml',
        'views/medical_cabinet_views.xml',
        'views/laboratory_org_views.xml',
        'views/pharmacy_org_views.xml',
        'views/sanad_ai_log_views.xml',
        'views/sanad_menus.xml',
    ],
    'demo': [
        'data/sanad_core_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
