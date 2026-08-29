# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Exposes the pluggable AI provider configuration in
    Settings > General Settings, backed by ir.config_parameter (the
    standard Odoo mechanism for this kind of deployment-level config).
    Changing these values never requires a code change or a module
    update - this is what makes the provider swappable at runtime."""
    _inherit = 'res.config.settings'

    sanad_ai_provider = fields.Selection([
        ('mock', 'Mock / Offline (no external calls)'),
        ('anthropic', 'Anthropic'),
        ('openai', 'OpenAI'),
    ], string='AI Provider', config_parameter='sanad_ai.provider', default='mock')
    sanad_ai_api_key = fields.Char(
        string='AI Provider API Key', config_parameter='sanad_ai.api_key',
        help='Stored as a system parameter. Leave empty to use the mock provider.')
    sanad_ai_model = fields.Char(
        string='AI Model Name', config_parameter='sanad_ai.model',
        help='e.g. claude-sonnet-4-6 for Anthropic, gpt-4o-mini for OpenAI.')
