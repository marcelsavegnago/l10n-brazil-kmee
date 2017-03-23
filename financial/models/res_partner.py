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
        # store=True,
        compute='_compute_available_credit_limit',
    )
    credit = fields.Monetary(
        # store=True,
    )
    @api.depends('credit_limit', 'credit')
    def _compute_available_credit_limit(self):
        # FIXME
        # config = self.env['account.config.settings']
        draft_inv = 0
        sale_ord = 0
        for record in self:
            record.available_credit_limit = record.credit_limit - record.credit
            # if config.confirmed_orders:
            sale_env = self.env['sale.order'].search([(
                'partner_id', '=', record.id)])
            for records in sale_env:
                if records.state == 'sale':
                    sale_ord += records.amount_total
            #     record.available_credit_limit -= partner.confirmed_ord
            # if config.draft_invoices:
            invoice_env = self.env['account.invoice'].search([(
                'commercial_partner_id', '=', record.id)])
            for records in invoice_env:
                if records.state == 'draft':
                    draft_inv += records.amount_total_signed
        print draft_inv
        print sale_ord
                # record.available_credit_limit -= partner.draft_inv


    # @api.multi
    # def _credit_debit_get(self):
    #     tables, where_clause, where_params = self.env['account.move.line']._query_get()
    #     where_params = [tuple(self.ids)] + where_params
    #     if where_clause:
    #         where_clause = 'AND ' + where_clause
    #     self._cr.execute("""SELECT account_move_line.partner_id, act.type, SUM(account_move_line.amount_residual)
    #                   FROM account_move_line
    #                   LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
    #                   LEFT JOIN account_account_type act ON (a.user_type_id=act.id)
    #                   WHERE act.type IN ('receivable','payable')
    #                   AND account_move_line.partner_id IN %s
    #                   AND account_move_line.reconciled IS FALSE
    #                   """ + where_clause + """
    #                   GROUP BY account_move_line.partner_id, act.type
    #                   """, where_params)
    #     for pid, type, val in self._cr.fetchall():
    #         partner = self.browse(pid)
    #         if type == 'receivable':
    #             partner.credit = val
    #         elif type == 'payable':
    #             partner.debit = -val
    #     print partner.credit
    #     print partner.debit