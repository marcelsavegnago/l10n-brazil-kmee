# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import division, print_function, unicode_literals

from openerp import api, fields, models, _

BANDEIRA_CARTAO = (
    ('01', 'Visa'),
    ('02', 'Mastercard'),
    ('03', 'American Express'),
    ('04', 'Sorocred'),
    ('05', 'Diners Club'),
    ('06', 'Elo'),
    ('07', 'Hipercard'),
    ('08', 'Aura'),
    ('09', 'Cabal'),
    ('99', 'Outros'),
)
BANDEIRA_CARTAO_DICT = dict(BANDEIRA_CARTAO)

BANDEIRA_CARTAO_VISA = '01'
BANDEIRA_CARTAO_MASTERCARD = '02'
BANDEIRA_CARTAO_AMERICAN_EXPRESS = '03'
BANDEIRA_CARTAO_SOROCRED = '04'
BANDEIRA_CARTAO_DINERS_CLUB = '05'
BANDEIRA_CARTAO_ELO = '06'
BANDEIRA_CARTAO_HIPERCARD = '07'
BANDEIRA_CARTAO_AURA = '08'
BANDEIRA_CARTAO_CABAL = '09'
BANDEIRA_CARTAO_OUTROS = '99'

INTEGRACAO_CARTAO = (
    ('1', 'Integrado'),
    ('2', 'Não integrado'),
)
INTEGRACAO_CARTAO_INTEGRADO = '1'
INTEGRACAO_CARTAO_NAO_INTEGRADO = '2'

FORMA_PAGAMENTO = (
    ('01', 'Dinheiro'),
    ('02', 'Cheque'),
    ('03', 'Cartão de crédito'),
    ('04', 'Cartão de débito'),
    ('05', 'Crédito na loja'),
    ('10', 'Vale alimentação'),
    ('11', 'Vale refeição'),
    ('12', 'Vale presente'),
    ('13', 'Vale combustível'),
    ('14', 'Duplicata mercantil'),
    ('15', 'Boleto bancário'),
    ('90', 'Sem pagamento'),
    ('99', 'Outros'),
)


class AccountInvoicePayment(models.Model):
    _name = b'account.invoice.payment'
    _description = 'Account Invoice Payment'
    _order = 'invoice_id, sequence, payment_term_id'

    sequence = fields.Integer(
        default=10,
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Condição de pagamento',
        ondelete='restrict',
        # domain=[('forma_pagamento', '!=', False)],
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
    )
    amount = fields.Float(
        string='Amount',
    )
    autorizacao = fields.Char(
        string='Autorização nº',
        size=20,
    )
    nsu = fields.Char(
        string='NSU',
        help='Numero sequencial unico',
    )
    forma_pagamento = fields.Selection(
        selection=FORMA_PAGAMENTO,
        string='Forma de pagamento',
    )
    card_brand = fields.Selection(
        selection=BANDEIRA_CARTAO,
        string='Bandeira do cartão',
    )
    card_integration = fields.Selection(
        selection=INTEGRACAO_CARTAO,
        string='Integração do cartão',
        default=INTEGRACAO_CARTAO_NAO_INTEGRADO,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Operadora do cartão',
        ondelete='restrict',
    )
    cnpj_cpf = fields.Char(
        string='CNPJ/CPF',
        size=18,
        related='partner_id.cnpj_cpf',
        readonly=True,
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        ondelete='set null',  # Allow use the same model in sale and purchase
    )
    item_ids = fields.One2many(
        comodel_name='account.invoice.payment.line',
        inverse_name='payment_id',
        string='Duplicatas',
    )

    @api.onchange('payment_term_id', 'amount', 'item_ids')
    def _onchange_payment_term_id(self):

        if not (self.payment_term_id and self.amount and
                self.env.context.get('field_parent')):
            return

        field_parent = self.env.context.get('field_parent')
        field_parent_id = getattr(self, field_parent)

        if field_parent == 'invoice_id':
            date = field_parent_id.date_invoice
            self.invoice_id = field_parent_id
        # TODO: Implementar para vendas e compras

        pterm_list = self.payment_term_id.compute(self.amount, date)[0]

        item_ids = []

        for i, item in enumerate(pterm_list):
            item_ids.append(
                (0, 0, {
                    'payment_id': self.id,
                    'number': i + 1,
                    'date_due': item[0],
                    'amount': item[1],
                })
            )
        self.item_ids = item_ids
