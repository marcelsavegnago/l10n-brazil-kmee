# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import (division, print_function, unicode_literals,
                        absolute_import)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FinanceiroCheque(models.Model):

    _name = b'financeiro.cheque'
    _description = 'Cadastrar Cheques'

    name = fields.Char(
        compute='_compute_name'
    )
    notes = fields.Text()

    financial_move_ids = fields.One2many(
        string=u'Pagamentos',
        comodel_name='financial.move',
        inverse_name='cheque_id',
        readonly=True,
    )
    participante_id = fields.Many2one(
        comodel_name='sped.participante',
        string='Pagador',
        ondelete='set null',
        index=True,
    )
    codigo = fields.Char(
        string=u'Código de Barras'
    )
    banco_id = fields.Many2one(
        comodel_name='res.bank',
        string=u'Banco'
    )
    agencia = fields.Many2one(
        string=u'Agência',
        comodel_name='res.bank.agencia'
    )
    conta = fields.Char(
        string=u'Conta Corrente'
    )
    titular = fields.Char(
        string=u'Nome de titular'
    )
    cpf_titular = fields.Char(
        string=u'CPF/CNPJ Titular'
    )
    valor = fields.Float(
        string=u'Valor',
        digits=(16, 2)
    )
    numero_cheque = fields.Char(
        string=u'Número do cheque'
    )
    pre_datado = fields.Date(
        string=u'Pré datado para'
    )
    data_recebimento = fields.Date(
        string=u'Data do recebimento',
        default=fields.Date.today,
    )
    state = fields.Selection(
        selection=[
            ('novo', u'Novo'),
            ('recebido', u'Recebido'),
            ('depositado', u'Depositado'),
            ('repassado', u'Repassado'),
            ('devolvido_b', u'Devolvido pelo banco'),
            ('devolvido_p', u'Devolvido ao parceiro'),
        ],
        string='Status',
        default='novo',
    )

    valor_residual = fields.Float(
        string=u'Valor residual',
    )

    empresa_id = fields.Many2one(
        comodel_name='sped.empresa',
        string='Empresa',
        ondelete='restrict',
        compute='_compute_empresa',
    )

    partner_bank_id = fields.Many2one(
        string='Conta atual',
        comodel_name='res.partner.bank',
        required=True,
    )

    def mudar_estado(self, estado):
        permitido = [
            ('novo', 'recebido'),
            ('recebido', 'depositado'),
            ('recebido', 'repassado'),
            ('recebido', 'devolvido_b'),
            ('devolvido_b', 'devolvido_p')
        ]
        if (self.state, estado) in permitido:
            self.state = estado
        else:
            raise UserError(_("Mudança do estado \"%s\" para estado \"%s\" "
                              "não permitida.") % (self.state, estado))

    def button_receber_cheque(self):
        self.mudar_estado('recebido')

    def button_depositar_cheque(self):
        self.mudar_estado('depositado')

    def button_repassar_cheque(self):
        self.mudar_estado('repassado')

    def button_devolver_cheque_banco(self):
        self.mudar_estado('devolvido_b')

    def button_devolver_cheque_parceiro(self):
        self.mudar_estado('devolvido_p')

    @api.onchange('codigo')
    def onchange_codigo(self):
        if self.codigo and len(self.codigo) >= 30:
            self.banco_id = self.env.get('res.bank').search([
                ('bic', '=', self.codigo[:3])
            ])
            if not self.banco_id:
                raise UserError(_("Não foi encontrado banco com código %s")
                                % self.codigo[:3])
            self.agencia = self.env.get('res.bank.agencia').search([
                ('name', '=', self.codigo[3:7]),
                ('banco_id', '=', self.banco_id.id)
            ])
            if not self.agencia:
                raise UserError(_("Nenhuma agência %s referente ao %s")
                                % (self.codigo[3:7], self.banco_id.name))
            self.numero_cheque = self.codigo[11:17]
            self.conta = self.codigo[22:-2] + '-' + self.codigo[-2]

    @api.onchange('valor')
    def _set_valor_residual(self):
        self.valor_residual = self.valor

    @api.depends('partner_bank_id')
    def _compute_empresa(self):
        for record in self:
            if self.partner_bank_id:
                self.empresa_id = \
                    self.partner_bank_id.company_id.sped_empresa_id

    @api.depends('participante_id')
    def _compute_name(self):
        for record in self:
            if record.participante_id and record.numero_cheque:
                record.name = 'CHQ - ' + record.numero_cheque or '' + \
                              ' - ' + record.participante_id.display_name or ''