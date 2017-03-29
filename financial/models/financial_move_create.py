# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class FinancialMove(models.Model):
    _inherit = 'financial.move'



    @api.depends('payment_mode_id', 'payment_term_id', 'amount_total',
                 'partner_id')
    def _mount_domain(self):

        payment_mode_ids = []
        payment_term_ids = []
        mode = self.env['account.payment.mode'].search([
            ('liquidity', '=', False)])
        payment_mode_ids.append(mode.ids)

        term = self.env['account.payment.term'].search([
            ('installments', '=', False)])
        payment_term_ids.append(term.ids)

        if self.amount_total <= self.partner_id.available_credit_limit:
            mode = self.env['account.payment.mode'].search([
                ('liquidity', '=', True)])
            payment_mode_ids.append(mode.ids)
            term = self.env['account.payment.term'].search([
                ('installments', '=', True)])
            payment_term_ids.append(term.ids)

        self.payment_term_domain = str(payment_term_ids)
        self.payment_mode_domain = str(payment_mode_ids)
