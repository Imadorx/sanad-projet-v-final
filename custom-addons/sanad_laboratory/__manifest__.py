# -*- coding: utf-8 -*-
{
    'name': 'SANAD Laboratory',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Laboratory analysis workflow and KPI tracking',
    'description': """
SANAD Laboratory
=================
Laboratory analysis workflow module (PRD 5.4 / 10.4).

Provides:
- sanad.lab.request: analysis request raised by a doctor, routed to a
  laboratory, with a status workflow (Draft -> Sent -> Accepted ->
  Processing -> Completed / Cancelled) matching the PRD exactly
- sanad.lab.result: result values uploaded by the laboratory, linked
  back to the request and patient, with reference ranges and documents
- KPI evolution tracking: compare a patient's results for the same
  analysis type over time (PRD 10.4 example: Jan 120, Feb 115, Mar 105)
- Laboratory users only see requests routed to their own organization;
  doctors only see requests for patients they have an active care
  relationship with
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core', 'sanad_patient', 'sanad_medical'],
    'data': [
        'security/ir.model.access.csv',
        'security/sanad_laboratory_record_rules.xml',
        # sanad_lab_result_views.xml defines action_sanad_lab_result, which
        # sanad_lab_request_views.xml references in a stat-button - must
        # load first.
        'views/sanad_lab_result_views.xml',
        'views/sanad_lab_request_views.xml',
        'views/sanad_laboratory_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
