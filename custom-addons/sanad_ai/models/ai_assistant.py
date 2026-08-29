# -*- coding: utf-8 -*-
"""SANAD AI orchestration.

This is the single entry point every AI feature (search/explain/
translate/tts) routes through, so the pipeline order is enforced in one
place rather than re-implemented per feature:

    1. AUTHORIZATION  - can this user access this data at all? Uses the
       normal ORM search (record rules apply automatically); if the
       target record isn't found under the caller's access, the request
       is BLOCKED before any AI call is made.
    2. ANONYMIZATION   - services.anonymizer strips/masks identifiers
       from anything that will be sent to an external provider.
    3. PROVIDER CALL    - services.ai_provider.get_provider() (pluggable,
       configured via System Parameters).
    4. OUTPUT SAFETY    - services.safety_filter scans the response for
       diagnostic/prescriptive language; unsafe responses are BLOCKED
       and never shown to the user.
    5. AUDIT LOGGING    - every attempt (success/failed/blocked) is
       written to sanad.ai.log via sudo(), regardless of outcome.
"""
import logging

from odoo import models
from odoo.exceptions import AccessError, UserError

from ..services.anonymizer import (
    anonymize_text, build_replacement_map, anonymize_patient_summary,
)
from ..services.ai_provider import get_provider, AIProviderError, SAFETY_SYSTEM_PROMPT
from ..services.safety_filter import check_response_safety, finalize_response

_logger = logging.getLogger(__name__)


class SanadAiAssistant(models.AbstractModel):
    _name = 'sanad.ai.assistant'
    _description = 'SANAD AI Assistant Orchestration'

    # ------------------------------------------------------------------
    # Audit logging helper
    # ------------------------------------------------------------------
    def _log(self, request_type, request_text, status, accessed_model=None,
              accessed_record_ids=None, anonymization_applied=False,
              response_metadata=None):
        """Writes to sanad.ai.log via sudo() - per the Phase 1 design,
        no security group has direct write access to this model; only
        this server-side path (running as the system user) can create
        audit rows, keeping the trail tamper-resistant from the app layer."""
        self.env['sanad.ai.log'].sudo().create({
            'user_id': self.env.uid,
            'request_type': request_type,
            'request_text': (request_text or '')[:2000],
            'accessed_model': accessed_model,
            'accessed_record_ids': ','.join(str(i) for i in accessed_record_ids) if accessed_record_ids else False,
            'anonymization_applied': anonymization_applied,
            'response_metadata': response_metadata,
            'status': status,
        })

    def _get_doctor_patient_context(self, patient_id=None):
        patient = None
        if patient_id:
            patient = self.env['sanad.patient'].search([('id', '=', patient_id)], limit=1)
        doctor = self.env['sanad.doctor'].search([('user_id', '=', self.env.uid)], limit=1)
        return patient, doctor

    # ------------------------------------------------------------------
    # Feature 1: Authorized Search
    # ------------------------------------------------------------------
    def authorized_search(self, query, patient_id=None):
        """Searches the caller's authorized consultations, prescriptions
        and lab results for text matching `query`, then asks the AI
        provider to summarize the (anonymized) matches in plain
        language. If patient_id is given but not accessible to the
        caller, the request is blocked outright - no provider call is
        made and no data is included in the log beyond the fact that it
        was blocked."""
        if patient_id:
            patient = self.env['sanad.patient'].search([('id', '=', patient_id)], limit=1)
            if not patient:
                self._log('search', query, 'blocked', accessed_model='sanad.patient')
                raise AccessError(
                    'You are not authorized to search data for this patient.')

        domain_patient = [('patient_id', '=', patient_id)] if patient_id else []
        consultations = self.env['sanad.consultation'].search(
            domain_patient + [('reason', 'ilike', query)], limit=10)
        prescriptions = self.env['sanad.prescription'].search(
            domain_patient + [('medication', 'ilike', query)], limit=10)
        lab_results = self.env['sanad.lab.result'].search(
            (domain_patient and [('patient_id', '=', patient_id)] or [])
            + [('analysis_name', 'ilike', query)], limit=10)

        accessed_ids = consultations.ids + prescriptions.ids + lab_results.ids
        if not accessed_ids:
            self._log('search', query, 'success', accessed_model='multiple',
                       accessed_record_ids=[], anonymization_applied=False,
                       response_metadata='no_matches')
            return {'matches': [], 'summary': 'No authorized records matched your search.'}

        replacement_map = build_replacement_map(
            patient=self.env['sanad.patient'].browse(patient_id) if patient_id else None)
        context_lines = []
        for c in consultations:
            context_lines.append(f'Consultation: reason={c.reason}, date={c.date}')
        for p in prescriptions:
            context_lines.append(f'Prescription: medication={p.medication}, dosage={p.dosage}')
        for r in lab_results:
            context_lines.append(
                f'Lab result: {r.analysis_name}={r.result_value}{r.unit or ""} '
                f'(range {r.reference_range or "n/a"})')
        raw_context = '\n'.join(context_lines)
        anon_context, anonymized = anonymize_text(raw_context, replacement_map)

        prompt = (
            f'A user searched their authorized medical records for: "{query}".\n'
            f'Here are the matching authorized records (already anonymized):\n'
            f'{anon_context}\n\n'
            'Summarize these matches factually in plain language. Do not add '
            'any interpretation, diagnosis, or recommendation beyond what is '
            'literally stated in the records above.'
        )

        try:
            provider = get_provider(self.env)
            raw_response = provider.generate(prompt, system_prompt=SAFETY_SYSTEM_PROMPT)
        except AIProviderError as e:
            self._log('search', query, 'failed', accessed_model='multiple',
                       accessed_record_ids=accessed_ids, anonymization_applied=anonymized,
                       response_metadata=str(e)[:500])
            raise UserError('The AI search service is temporarily unavailable. Please try again later.') from e

        is_safe, matched_pattern = check_response_safety(raw_response)
        if not is_safe:
            self._log('search', query, 'blocked', accessed_model='multiple',
                       accessed_record_ids=accessed_ids, anonymization_applied=anonymized,
                       response_metadata=f'output_blocked:{matched_pattern}')
            return {
                'matches': [], 'blocked': True,
                'summary': 'This response was blocked by the AI safety filter. '
                            'Please consult your doctor directly for this question.',
            }

        final_response = finalize_response(raw_response)
        self._log('search', query, 'success', accessed_model='multiple',
                   accessed_record_ids=accessed_ids, anonymization_applied=anonymized,
                   response_metadata='provider_call_ok')
        return {
            'matches': [
                {'type': 'consultation', 'id': c.id, 'reason': c.reason} for c in consultations
            ] + [
                {'type': 'prescription', 'id': p.id, 'medication': p.medication} for p in prescriptions
            ] + [
                {'type': 'lab_result', 'id': r.id, 'analysis_name': r.analysis_name} for r in lab_results
            ],
            'summary': final_response,
        }

    # ------------------------------------------------------------------
    # Feature 2: Explanation
    # ------------------------------------------------------------------
    def explain_record(self, model_name, record_id):
        """Explains a single authorized record (consultation or lab
        result) in plain language. Only these two models are permitted
        targets - an arbitrary model_name is rejected outright."""
        allowed_models = {'sanad.consultation', 'sanad.lab.result'}
        if model_name not in allowed_models:
            self._log('explain', f'{model_name}#{record_id}', 'blocked')
            raise UserError('Explanation is only available for consultations and lab results.')

        record = self.env[model_name].search([('id', '=', record_id)], limit=1)
        if not record:
            self._log('explain', f'{model_name}#{record_id}', 'blocked', accessed_model=model_name)
            raise AccessError('You are not authorized to view this record.')

        patient = record.patient_id
        doctor = getattr(record, 'doctor_id', False)
        replacement_map = build_replacement_map(patient=patient, doctor=doctor or None)

        if model_name == 'sanad.consultation':
            raw_context = (
                f'Reason for visit: {record.reason}\n'
                f'Symptoms: {record.symptoms or "not recorded"}\n'
                f'Observations: {record.observations or "not recorded"}'
            )
        else:  # sanad.lab.result
            raw_context = (
                f'Analysis: {record.analysis_name}\n'
                f'Result: {record.result_value} {record.unit or ""}\n'
                f'Reference range: {record.reference_range or "not provided"}'
            )

        anon_context, anonymized = anonymize_text(raw_context, replacement_map)
        patient_summary = anonymize_patient_summary(patient) if patient else {}

        prompt = (
            'Explain the following medical information to a patient in simple, '
            'reassuring, plain language. The patient context (no identifying '
            f'info) is: {patient_summary}.\n\nInformation to explain:\n{anon_context}\n\n'
            'Do not diagnose. Do not recommend any treatment or medication. '
            'Only explain what the terms and values mean in general.'
        )

        try:
            provider = get_provider(self.env)
            raw_response = provider.generate(prompt, system_prompt=SAFETY_SYSTEM_PROMPT)
        except AIProviderError as e:
            self._log('explain', f'{model_name}#{record_id}', 'failed',
                       accessed_model=model_name, accessed_record_ids=[record_id],
                       anonymization_applied=anonymized, response_metadata=str(e)[:500])
            raise UserError('The AI explanation service is temporarily unavailable.') from e

        is_safe, matched_pattern = check_response_safety(raw_response)
        if not is_safe:
            self._log('explain', f'{model_name}#{record_id}', 'blocked',
                       accessed_model=model_name, accessed_record_ids=[record_id],
                       anonymization_applied=anonymized,
                       response_metadata=f'output_blocked:{matched_pattern}')
            return {'blocked': True,
                    'explanation': 'This explanation was blocked by the AI safety filter. '
                                    'Please ask your doctor to explain this result.'}

        final_response = finalize_response(raw_response)
        self._log('explain', f'{model_name}#{record_id}', 'success',
                   accessed_model=model_name, accessed_record_ids=[record_id],
                   anonymization_applied=anonymized, response_metadata='provider_call_ok')
        return {'explanation': final_response}

    # ------------------------------------------------------------------
    # Feature 3: Translation
    # ------------------------------------------------------------------
    def translate_text(self, text, target_lang):
        """Translates arbitrary user-supplied text (typically an earlier
        AI explanation, or a document excerpt the patient pasted in).
        Still passed through the anonymizer as a defense-in-depth
        measure in case the pasted text contains identifiers, even
        though it did not originate from a known ORM record this time."""
        supported = {'ar': 'Arabic', 'fr': 'French', 'en': 'English'}
        if target_lang not in supported:
            raise UserError('Unsupported target language. Supported: ar, fr, en.')

        anon_text, anonymized = anonymize_text(text)
        prompt = (
            f'Translate the following medical information into {supported[target_lang]}. '
            'Preserve the factual meaning exactly. Do not add, remove, or '
            'reinterpret any medical content.\n\n' + anon_text
        )

        try:
            provider = get_provider(self.env)
            raw_response = provider.generate(prompt, system_prompt=SAFETY_SYSTEM_PROMPT)
        except AIProviderError as e:
            self._log('translate', text, 'failed', anonymization_applied=anonymized,
                       response_metadata=str(e)[:500])
            raise UserError('The AI translation service is temporarily unavailable.') from e

        is_safe, matched_pattern = check_response_safety(raw_response)
        if not is_safe:
            self._log('translate', text, 'blocked', anonymization_applied=anonymized,
                       response_metadata=f'output_blocked:{matched_pattern}')
            return {'blocked': True, 'translation': 'Translation blocked by safety filter.'}

        self._log('translate', text, 'success', anonymization_applied=anonymized,
                   response_metadata=f'target_lang:{target_lang}')
        return {'translation': raw_response, 'target_lang': target_lang}

    # ------------------------------------------------------------------
    # Feature 4: Text-to-Speech
    # ------------------------------------------------------------------
    def request_tts(self, text):
        """SANAD does not run a server-side speech-synthesis engine by
        default (no such credentials/service is assumed to be
        available). Rather than fake audio generation, this returns a
        'browser' mode instructing the frontend to use the standard Web
        Speech API (window.speechSynthesis) - a real, working
        accessibility feature with zero added infrastructure. A future
        server-side provider can be added the same way ai_provider.py
        is pluggable, without changing this method's contract (it would
        just return {'mode': 'audio_url', 'audio_url': ...} instead).
        """
        anon_text, anonymized = anonymize_text(text)
        self._log('tts', text, 'success', anonymization_applied=anonymized,
                   response_metadata='mode:browser')
        return {'mode': 'browser', 'text': anon_text}
