# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import division, print_function, unicode_literals

from openerp import api, fields, models, _



class AccountInvoicePaymentLine(models.Model):

    _name = b'account.invoice.payment.line'
    _description = 'Payment Lines'
    _order = 'invoice_id, date_due'
    _rec_name = 'number'

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        ondelete='set null', # Allow use the same model in sale and purchase
    )
    payment_id = fields.Many2one(
        comodel_name='account.invoice.payment',
        string='Pagamento',
        ondelete='cascade',
    )
    number = fields.Char(
        string='Número',
        size=60,
        required=True,
    )
    date_due = fields.Date(
        string='Data de vencimento',
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        # related='payment_id.currency_id',
        store=True,
    )
    amount = fields.Float(
        string='Valor',
        digits=(18, 2),
        required=True,
    )
