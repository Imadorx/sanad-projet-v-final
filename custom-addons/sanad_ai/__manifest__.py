# -*- coding: utf-8 -*-
{
    'name': 'SANAD AI',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - AI assistant with PHI protection and safety enforcement',
    'description': """
SANAD AI
========
AI integration module (PRD Section 15 / 10.7).

Provides four AI-assisted capabilities, all strictly informational:
- Authorized search over a user's own accessible medical data
- Explanation of medical documents/results in plain language
- Translation into the patient's preferred language (AR/FR/EN)
- Text-to-speech generation for accessibility

Hard safety constraints (non-negotiable, enforced in code, not just
prompted):
  AI MUST NEVER diagnose, prescribe, or replace a healthcare professional.
  AI ONLY explains, searches, translates, or summarizes information the
  requesting user is already authorized to see.

Every request passes through, in order:
  1. Authorization check (can this user access this data at all?)
  2. PHI anonymization (patient identifiers stripped/masked before any
     data leaves the platform for an external AI provider)
  3. Safety-classified prompt construction (system prompt hard-codes the
     never-diagnose/never-prescribe constraints)
  4. Provider call (pluggable - see services/ai_provider.py)
  5. Output safety check (response scanned for diagnostic/prescriptive
     language before being returned to the user)
  6. Audit logging to sanad.ai.log (status: success/failed/blocked)

The AI provider is configurable via System Parameters
(sanad_ai.provider, sanad_ai.api_key, sanad_ai.model) so the underlying
LLM can be swapped without code changes - see services/ai_provider.py.
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core', 'sanad_patient', 'sanad_medical', 'sanad_laboratory'],
    'data': [
        'security/ir.model.access.csv',
        'data/sanad_ai_config_data.xml',
        'views/sanad_ai_config_views.xml',
        'views/sanad_ai_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
