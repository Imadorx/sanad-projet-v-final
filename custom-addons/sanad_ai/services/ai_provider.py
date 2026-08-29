# -*- coding: utf-8 -*-
"""Pluggable AI provider abstraction.

The PRD requires the AI architecture to allow changing the LLM provider
later without a rewrite. Every provider implements the same minimal
interface (generate()); which one is active is a System Parameter
(sanad_ai.provider), not a code branch scattered through business
logic. Adding a new provider means adding one class here and one entry
in PROVIDER_REGISTRY - nothing else in sanad_ai changes.

Providers never receive raw PHI: by the time a prompt reaches
provider.generate(), it has already passed through
services.anonymizer.anonymize_text(). This module has no knowledge of
Odoo records at all, by design - it only ever sees already-anonymized
strings, which makes it impossible for a future provider integration to
accidentally bypass the anonymization layer.
"""
import json
import logging

import requests

_logger = logging.getLogger(__name__)

SAFETY_SYSTEM_PROMPT = (
    "You are a medical information assistant embedded in a healthcare "
    "platform. You operate under strict, non-negotiable rules:\n"
    "1. You must NEVER diagnose a medical condition.\n"
    "2. You must NEVER recommend, suggest, or prescribe any medication, "
    "dosage, or treatment.\n"
    "3. You must NEVER tell the user what they should do medically, or "
    "imply a course of action a doctor should take.\n"
    "4. You must NEVER replace the judgment of a healthcare professional.\n"
    "5. You may ONLY explain existing information already provided to "
    "you in plain language, translate it, or summarize it factually.\n"
    "6. You must always note that this information is educational and "
    "encourage the user to consult their healthcare professional for any "
    "medical decision.\n"
    "7. All patient-identifying information has already been removed "
    "from any data you receive - do not attempt to infer or guess "
    "identities, and do not request identifying information.\n"
    "If a request asks you to diagnose, prescribe, or give medical "
    "advice beyond explaining existing information, politely decline "
    "and explain that this platform's AI assistant cannot do that."
)


class AIProviderError(Exception):
    """Raised on any provider-level failure (network, auth, malformed
    response) so calling code can log status='failed' distinctly from
    status='blocked' (safety refusal) or status='success'."""


class BaseAIProvider:
    def generate(self, user_prompt, system_prompt=None, max_tokens=800):
        raise NotImplementedError


class MockAIProvider(BaseAIProvider):
    """Deterministic offline provider used when no external API key is
    configured (default out-of-the-box state, and used in automated
    tests). It is explicitly labeled as a stub in its own output so it
    can never be mistaken for a real clinical explanation - this is a
    development/testing fallback, not a disguised fake feature."""

    def generate(self, user_prompt, system_prompt=None, max_tokens=800):
        return (
            "[SANAD AI - offline/mock provider active] No external AI "
            "provider is configured, so this is a placeholder response. "
            "Configure sanad_ai.provider, sanad_ai.api_key and "
            "sanad_ai.model in Settings > Technical > Parameters to "
            "enable real AI responses. Your anonymized request was: "
            f"{user_prompt[:300]}"
        )


class AnthropicProvider(BaseAIProvider):
    def __init__(self, api_key, model='claude-sonnet-4-6'):
        self.api_key = api_key
        self.model = model

    def generate(self, user_prompt, system_prompt=None, max_tokens=800):
        try:
            resp = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': self.api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json',
                },
                json={
                    'model': self.model,
                    'max_tokens': max_tokens,
                    'system': system_prompt or SAFETY_SYSTEM_PROMPT,
                    'messages': [{'role': 'user', 'content': user_prompt}],
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            parts = [b.get('text', '') for b in data.get('content', []) if b.get('type') == 'text']
            return '\n'.join(parts).strip()
        except requests.RequestException as e:
            _logger.error('Anthropic provider call failed: %s', e)
            raise AIProviderError(str(e)) from e
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            _logger.error('Anthropic provider returned unexpected response: %s', e)
            raise AIProviderError('Malformed provider response') from e


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key, model='gpt-4o-mini'):
        self.api_key = api_key
        self.model = model

    def generate(self, user_prompt, system_prompt=None, max_tokens=800):
        try:
            resp = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'max_tokens': max_tokens,
                    'messages': [
                        {'role': 'system', 'content': system_prompt or SAFETY_SYSTEM_PROMPT},
                        {'role': 'user', 'content': user_prompt},
                    ],
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            return data['choices'][0]['message']['content'].strip()
        except requests.RequestException as e:
            _logger.error('OpenAI provider call failed: %s', e)
            raise AIProviderError(str(e)) from e
        except (KeyError, IndexError, ValueError, json.JSONDecodeError) as e:
            _logger.error('OpenAI provider returned unexpected response: %s', e)
            raise AIProviderError('Malformed provider response') from e


PROVIDER_REGISTRY = {
    'mock': MockAIProvider,
    'anthropic': AnthropicProvider,
    'openai': OpenAIProvider,
}


def get_provider(env):
    """Factory: reads sanad_ai.provider / sanad_ai.api_key / sanad_ai.model
    from ir.config_parameter and instantiates the matching provider.
    This is the ONLY place provider selection happens - business logic
    in models/ai_assistant.py never checks provider type directly."""
    get_param = env['ir.config_parameter'].sudo().get_param
    provider_name = get_param('sanad_ai.provider', default='mock')
    provider_cls = PROVIDER_REGISTRY.get(provider_name, MockAIProvider)

    if provider_name == 'mock':
        return MockAIProvider()

    api_key = get_param('sanad_ai.api_key', default=False)
    model = get_param('sanad_ai.model', default=False)
    if not api_key:
        _logger.warning(
            'sanad_ai.provider is set to "%s" but no API key is configured; '
            'falling back to the mock provider.', provider_name)
        return MockAIProvider()

    kwargs = {'api_key': api_key}
    if model:
        kwargs['model'] = model
    return provider_cls(**kwargs)
