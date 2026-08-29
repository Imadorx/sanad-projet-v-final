# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import ValidationError


class SanadPrescriptionPharmacyExtension(models.Model):
    """Extends sanad.prescription (sanad_medical) with the pharmacy-facing
    workflow actions (PRD 5.5 / 10.5: Received -> Prepared -> Completed).

    The pharmacy_status field and pharmacy_id assignment field already
    exist on the base model; this module only adds the state-transition
    methods and, in views/, a restricted view surface for pharmacy staff
    so they interact only with medication/dosage/instructions data
    (PRD 14.3: pharmacy cannot view medical records).
    """
    _inherit = 'sanad.prescription'

    def action_pharmacy_receive(self):
        for rx in self:
            if rx.pharmacy_status != 'pending':
                raise ValidationError('Only pending prescriptions can be received.')
            if not rx.pharmacy_id:
                raise ValidationError(
                    'This prescription has not been assigned to a pharmacy yet.')
            rx.pharmacy_status = 'received'

    def action_pharmacy_prepare(self):
        for rx in self:
            if rx.pharmacy_status != 'received':
                raise ValidationError('Only received prescriptions can move to prepared.')
            rx.pharmacy_status = 'prepared'

    def action_pharmacy_complete(self):
        for rx in self:
            if rx.pharmacy_status != 'prepared':
                raise ValidationError('Only prepared prescriptions can be completed.')
            rx.pharmacy_status = 'completed'
