# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SanadLabResult(models.Model):
    """Laboratory analysis result (PRD 10.4).

    Fields match the PRD exactly: analysis_name, result_value, unit,
    reference_range, document, date.

    Also provides the KPI evolution helper (PRD 10.4 "KPI Follow-up":
    compare Analysis 1..N over time, e.g. Jan 120, Feb 115, Mar 105)
    used by the patient/doctor dashboards to chart trends for a given
    analysis_name.
    """
    _name = 'sanad.lab.result'
    _description = 'SANAD Laboratory Result'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    _rec_name = 'display_name'

    request_id = fields.Many2one(
        'sanad.lab.request', string='Analysis Request', required=True,
        ondelete='cascade', index=True)
    patient_id = fields.Many2one(
        related='request_id.patient_id', string='Patient', store=True, readonly=True, index=True)

    analysis_name = fields.Char(string='Analysis Name', required=True, tracking=True)
    result_value = fields.Float(string='Result Value', required=True, tracking=True)
    unit = fields.Char(string='Unit')
    reference_range = fields.Char(string='Reference Range',
                                   help='e.g. "70-100 mg/dL"')
    document = fields.Binary(string='Result Document', attachment=True)
    document_filename = fields.Char(string='Document Filename')
    date = fields.Datetime(string='Result Date', default=fields.Datetime.now, required=True)

    is_out_of_range = fields.Boolean(
        string='Out of Range', compute='_compute_out_of_range',
        help='Best-effort flag computed by parsing a numeric "low-high" '
             'reference range. Always verify manually - this is a UI aid, '
             'not a clinical judgment.')

    display_name = fields.Char(compute='_compute_display_name')

    @api.depends('analysis_name', 'result_value', 'date')
    def _compute_display_name(self):
        for res in self:
            res.display_name = '%s: %s %s (%s)' % (
                res.analysis_name or '', res.result_value, res.unit or '',
                res.date.strftime('%Y-%m-%d') if res.date else '')

    @api.depends('result_value', 'reference_range')
    def _compute_out_of_range(self):
        for res in self:
            res.is_out_of_range = False
            if res.reference_range and '-' in res.reference_range:
                try:
                    low_str, high_str = res.reference_range.split('-', 1)
                    low, high = float(low_str.strip()), float(high_str.strip())
                    res.is_out_of_range = not (low <= res.result_value <= high)
                except (ValueError, TypeError):
                    pass

    @api.model
    def get_kpi_evolution(self, patient_id, analysis_name):
        """Return chronological (date, value, unit) tuples for a given
        patient + analysis_name, for KPI trend charting (PRD 10.4).
        Access control note: this is a plain search - it inherits the
        normal record rules of sanad.lab.result, so a doctor calling this
        for a patient outside their care relationship gets an empty
        result set rather than raw data leaking around the rule.
        """
        results = self.search([
            ('patient_id', '=', patient_id),
            ('analysis_name', '=', analysis_name),
        ], order='date asc')
        return [
            {'date': r.date, 'value': r.result_value, 'unit': r.unit}
            for r in results
        ]
