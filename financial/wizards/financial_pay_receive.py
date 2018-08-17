# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from openerp import api, fields, models
from ..constants import (
    FINANCIAL_TYPE,
    FINANCIAL_DEBT_2RECEIVE,
    FINANCIAL_DEBT_2PAY,
)


class FinancialPayreceive(models.TransientModel):
    _name = 'financial.pay_receive'

    date_payment = fields.Date(
        string='Data do Pagamento',
        required=True,
        default=fields.Date.context_today,
    )
    document_type_id = fields.Many2one(
        comodel_name='financial.document.type',
        string='Tipo do Documento',
        ondelete='restrict',
        index=True,
        required=True,
    )
    document_number = fields.Char(
        string='Número do Documento',
        index=True,
        required=True,
    )
    bank_id = fields.Many2one(
        'res.partner.bank',
        string=u'Conta Bancária',
        required=True,
    )
    date_credit_debit = fields.Date(
        string='Data Credito/debito',
    )
    amount_document = fields.Float(
        string=u'Valor',
        required=True
    )
    amount_discount = fields.Float(
        string=u'Desconto',
    )
    amount_interest = fields.Float(
        string=u'Juros',
    )
    amount_total = fields.Float(
        string='Total',
        compute='_compute_total_and_residual',
        store=True,
        digits=(18, 2),
    )
    type = fields.Selection(
        string='Financial Type',
        selection=FINANCIAL_TYPE,
        required=True,
        index=True,
    )
    type_view = fields.Selection(
        string='Financial Type',
        selection=FINANCIAL_TYPE,
        related='type',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
    )

    @api.depends('amount_document', 'amount_interest', 'amount_discount')
    def _compute_total_and_residual(self):
        for move in self:
            amount_total = move.amount_document
            amount_total += move.amount_interest
            amount_total -= move.amount_discount

            amount_paid_document = 0
            amount_paid_interest = 0
            amount_paid_discount = 0
            amount_paid_total = 0

            amount_residual = 0
            amount_cancel = 0
            amount_refund = 0

            if move.type in (FINANCIAL_DEBT_2RECEIVE, FINANCIAL_DEBT_2PAY):
                for payment in move.payment_ids:
                    amount_paid_document += payment.amount_document
                    amount_paid_interest += payment.amount_interest
                    amount_paid_discount += payment.amount_discount
                    amount_paid_total += payment.amount_total

                amount_residual = amount_total - amount_paid_document

                if move.date_cancel:
                    amount_cancel = amount_residual

                if amount_residual < 0:
                    amount_refund = amount_residual * -1
                    amount_residual = 0

            move.amount_total = amount_total
            move.amount_residual = amount_residual
            move.amount_cancel = amount_cancel
            move.amount_refund = amount_refund
            move.amount_paid_document = amount_paid_document
            move.amount_paid_interest = amount_paid_interest
            move.amount_paid_discount = amount_paid_discount
            move.amount_paid_total = amount_paid_total

    @api.model
    def default_get(self, vals):
        res = super(FinancialPayreceive, self).default_get(vals)
        active_id = self.env.context.get('active_id')
        if (self.env.context.get('active_model') == 'financial.move' and
                active_id):
            fm = self.env['financial.move'].browse(active_id)
            if fm.type == '2pay':
                res['type'] = 'payment_item'
            else:
                res['type'] = 'receipt_item'
            res['company_id'] = fm.company_id.id
            res['document_type_id'] = fm.document_type_id.id
            res['currency_id'] = fm.currency_id.id
            res['amount_document'] = fm.amount_residual
            res['company_id'] = fm.company_id.id
            res['bank_id'] = fm.bank_id.id
        return res

    @api.multi
    def doit(self):
        for wizard in self:
            active_id = self._context['active_id']
            account_financial = self.env['financial.move']

            financial_to_pay = account_financial.browse(active_id)

            values = {
                'date_maturity': financial_to_pay.date_maturity,
                'company_id': wizard.company_id.id,
                'currency_id': financial_to_pay.currency_id.id,
                'type': wizard.type,
                'partner_id': financial_to_pay.partner_id.id,
                'document_number': financial_to_pay.document_number,
                'date_document': wizard.date_payment,
                'bank_id': wizard.bank_id.id,
                'date_payment': wizard.date_payment,
                'amount_document': wizard.amount_document,
                'debt_id': active_id,
                'date_credit_debit': wizard.date_credit_debit,
                'account_id': financial_to_pay.account_id.id,
                'document_type_id': wizard.document_type_id.id,
            }
            financial = account_financial.create(values)
            financial.action_confirm()
