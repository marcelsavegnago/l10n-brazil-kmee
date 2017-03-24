# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResPartner(models.Model):

    _inherit = 'res.partner'

    credit_limit = fields.Monetary(
        string=_('Limite de Crédito'),
    )
    available_credit_limit = fields.Monetary(
        string=_('Available Credit Limit'),
        compute='_compute_available_credit_limit',
    )
    credit = fields.Monetary()

    @api.depends('credit_limit', 'credit')
    def _compute_available_credit_limit(self):
        # FIXME
        config = self.env['account.config.settings'].search([
            ('company_id', '=', 'self.env.user.company_id')])
        draft_inv = 0
        sale_ord = 0
        for record in self:
            record.available_credit_limit = record.credit_limit - record.credit
            if config.confirmed_orders:
                sale_env = self.env['sale.order'].search([(
                    'partner_id', '=', record.id)])
                for records in sale_env:
                    if records.state == 'sale':
                        sale_ord += records.amount_total
                    record.available_credit_limit -= sale_ord
            if config.draft_invoices:
                invoice_env = self.env['account.invoice'].search([(
                    'commercial_partner_id', '=', record.id)])
                for records in invoice_env:
                    if records.state == 'draft':
                        draft_inv += records.amount_total_signed
                record.available_credit_limit -= draft_inv
            print 'draft_inv' + draft_inv
            print 'sale_ord' + sale_ord
            print record.available_credit_limit
