# -*- coding: utf-8 -*-
{
    'name': 'SANAD Chat',
    'version': '19.0.1.0.0',
    'category': 'Healthcare/SANAD',
    'summary': 'SANAD Healthcare Platform - Secure real-time communication',
    'description': """
SANAD Chat
==========
Secure communication module (PRD 5.x / 10.6 / 16).

Supported conversations: Doctor<->Patient, Doctor<->Laboratory,
Doctor<->Pharmacy.

Implementation uses Odoo 19's native bus.bus longpolling/websocket
infrastructure for real-time delivery, per the approved architecture
decision - no separate messaging stack (Socket.io/Node service) is
introduced. Threads are backed by mail.thread on sanad.chat.conversation,
so messages, attachments and read-state reuse Odoo's mature mail
subsystem instead of a bespoke reimplementation.

Provides:
- sanad.chat.conversation: a conversation between two authorized SANAD
  users (only pairings allowed by the PRD are permitted - enforced in
  Python, not just the UI)
- Real-time delivery via bus.bus notifications
- Automatic activity-based notifications on new messages (PRD 17)
    """,
    'author': 'SANAD Development Team',
    'license': 'LGPL-3',
    'depends': ['sanad_core', 'sanad_patient', 'bus', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/sanad_chat_record_rules.xml',
        'views/sanad_chat_views.xml',
        'views/sanad_chat_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sanad_chat/static/src/js/sanad_chat_notifications.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
