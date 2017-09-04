# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import (division, print_function, unicode_literals,
                        absolute_import)

from odoo import fields, models


class FinanceiroMovimentacaoCheque(models.Model):

    _name = b'financeiro.movimentacao.cheque'
    _description = 'Depositos de Cheques'

    name = fields.Char()

    type = fields.Selection(
        string='Tipo de Movimentação',
        selection=[
            ('deposito', 'Depósito'),
            ('estorno', 'estorno'),
        ],
        help='Indica o tipo da movimentação.',
    )

    partner_bank_from_id = fields.Many2one(
        string='Origem',
        comodel_name='res.partner.bank',
        required=True,
    )

    partner_bank_to_id = fields.Many2one(
        string='Destino',
        comodel_name='res.partner.bank',
        required=True,
        domain="[('id', '!=', partner_bank_from_id)]",
    )

    cheque_ids = fields.Many2many(
        comodel_name='financeiro.cheque',
        string=u'Cheques',
    )

    financial_account_id = fields.Many2one(
        comodel_name='financial.account',
        string='Conta financeira',
        ondelete='restrict',
        required=True,
    )

    financial_ids = fields.One2many(
        comodel_name='financial.move',
        inverse_name='movimentacoes_cheque_id',
        string='Financial Items',
        readonly=True,
        copy=False,
    )

    data_deposito = fields.Date(
        string="Data do depósito",
        default=fields.Date.today,
    )

    qtd_financeiro_moves_in = fields.Integer(
        string="Entradas do Financeiro",
        compute='_compute_qtd_financials',
    )

    qtd_financeiro_moves_out = fields.Integer(
        string="Saídas do Financeiro",
        compute='_compute_qtd_financials',
    )

    def _compute_qtd_financials(self):
        qtd_financeiro_moves_in = 0
        qtd_financeiro_moves_out = 0
        for financial_move in self.financial_ids:
            if financial_move.type == 'money_in':
                qtd_financeiro_moves_in += 1
            if financial_move.type == 'money_out':
                qtd_financeiro_moves_out += 1
        self.qtd_financeiro_moves_in = qtd_financeiro_moves_in
        self.qtd_financeiro_moves_out = qtd_financeiro_moves_out

    def prepare_financial_move(self, type, cheque):
        """
        Preparar dict para criar lançamento
        :param movimento: 
        :return: dict - Dicionario para criação do 
        """
        document_type = self.env.ref('financial.DOCUMENTO_FINANCEIRO_CHEQUE')

        if type in ['money_out', '2receive']:
            res_partner_bank_id = self.partner_bank_from_id
        elif type == 'money_in':
            res_partner_bank_id = self.partner_bank_to_id

        return (dict(
            bank_id=res_partner_bank_id.id,
            amount=cheque.valor,
            amount_document=cheque.valor,
            date_maturity=self.data_deposito,
            partner_id=cheque.participante_id.id,
            document_number=cheque.numero_cheque,
            account_id=self.financial_account_id.id,
            document_type_id=document_type.id,
            type=type,
            movimentacoes_cheque_id=self.id,
            company_id=cheque.empresa_id.original_company_id.id,
            # currency_id=self.currency_euro.id,
            # account_type_id=self.type_receivable.id,
        ))

    def button_depositar_cheque(self):
        '''
        Função que executa as rotinas de depósito de um cheque
        :return: 
        '''
        financial_move = self.env['financial.move']
        for deposito in self:
            # Gerar movimentações e mudar situação de cada cheque
            for cheque in self.cheque_ids:
                cheque.button_depositar_cheque()

                # Para cada cheque depositado efetuar 2 movimentações
                # - Saida do caixa
                # - Entrada no Banco
                for type in ['money_in', 'money_out']:
                    vals = self.prepare_financial_move(type, cheque)
                    financial_move.create(vals)

    def button_extornar_cheque(self):
        '''
        Função que executa as rotinas de estorno de um cheque
        :return: 
        '''
        financial_move = self.env['financial.move']
        for estorno in self:
            for cheque in self.cheque_ids:
                cheque.button_devolver_cheque_banco()
                # Para extornar efetue 2 movimentações
                # - Saida do caixa
                # - Entrada no Banco
                for type in ['money_out', 'money_in']:
                    vals = self.prepare_financial_move(type, cheque)
                    financial_move.create(vals)

                # No caso do estorno, criar um registro 'a receber'
                type = '2receive'
                vals_a_receber = self.prepare_financial_move(type, cheque)
                financial_move.create(vals_a_receber)

    def button_ver_saidas(self):
        financial_ids = []
        for financial_move_id in self.financial_ids:
            if financial_move_id.type == 'money_out':
                financial_ids.append(financial_move_id.id)

        view_id = \
            self.env.ref('financial.financial_move_payment_receipt_item_form')

        return {
            'name': 'Saídas',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'financial.move',
            'type': 'ir.actions.act_window',
            'res_id': financial_ids[0],
            'context': self.env.context
        }

    def button_ver_entradas(self):
        financial_ids = []
        for financial_move_id in self.financial_ids:
            if financial_move_id.type == 'money_in':
                financial_ids.append(financial_move_id.id)

        view_id = \
            self.env.ref('financial.financial_move_payment_payment_item_form')

        return {
            'name': 'Entradas',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'res_model': 'financial.move',
            'type': 'ir.actions.act_window',
            'res_id': financial_ids[0],
            'context': self.env.context
        }
