# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import (division, print_function, unicode_literals,
                        absolute_import)

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.l10n_br_base.models.sped_base import SpedBase

_logger = logging.getLogger(__name__)

try:
    from email_validator import validate_email

    from pybrasil.inscricao import (formata_cnpj, formata_cpf,
                                    limpa_formatacao,
                                    valida_cnpj, valida_cpf)

except (ImportError, IOError) as err:
    _logger.debug(err)


class FinancialCheque(SpedBase, models.Model):
    _name = b'financial.cheque'
    _description = 'Cheques'

    name = fields.Char(
        compute='_compute_name',
        store=True,
        index=True,
    )
    #
    # Identificação do cheque
    #
    codigo_barras = fields.Char(
        string='Código de Barras',
    )
    bank_id = fields.Many2one(
        comodel_name='res.bank',
        string='Banco',
        ondelete='restrict',
        required=True,
    )
    agencia = fields.Char(
        string='Agência',
        size=5,
        required=True,
    )
    conta = fields.Char(
        string='Conta',
        size=14,
        required=True,
    )
    numero = fields.Char(
        string='Número',
        size=10,
        required=True,
    )
    titular_nome = fields.Char(
        string='Nome de titular',
        size=60,
        required=True,
    )
    titular_cnpj_cpf = fields.Char(
        string='CPF/CNPJ Titular',
        size=18,
        required=True,
    )
    data = fields.Date(
        string='Data do cheque',
        default=fields.Date.today,
        required=True,
    )
    municipio_id = fields.Many2one(
        comodel_name='sped.municipio',
        string='Praça',
        ondelete='restrict',
        required=True,
    )
    #
    # Datas e valores
    #
    data_entrada = fields.Date(
        string='Data de entrada',
        default=fields.Date.today,
        required=True,
        index=True,
    )
    data_pre_datado = fields.Date(
        string='Pré-datado para',
        index=True,
    )
    valor = fields.Monetary(
        string='Valor',
        required=True,
    )
    valor_libera_limite = fields.Monetary(
        string='Libera limite antes da compensação',
    )
    #
    # Quem deu o cheque
    #
    participante_original_id = fields.Many2one(
        comodel_name='sped.participante',
        string='Recebido de',
        ondelete='restrict',
        required=True,
        index=True,
    )
    #
    # Qual a situação do cheque
    #
    participante_atual_id = fields.Many2one(
        comodel_name='sped.participante',
        string='Em poder de',
        ondelete='restrict',
        compute='_compute_atual',
        store=True,
        index=True,
    )
    empresa_atual_id = fields.Many2one(
        comodel_name='sped.empresa',
        string='Empresa origem',
        compute='_compute_atual',
        store=True,
        index=True,
    )
    movimento_participante_atual_id = fields.Many2one(
        comodel_name='financial.cheque.movimento',
        string='Movimentação em poder de',
        compute='_compute_atual',
        store=True,
        index=True,
    )
    partner_bank_atual_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Conta/caixa atual',
        ondelete='restrict',
        compute='_compute_atual',
        store=True,
        index=True,
    )
    movimento_participante_atual_id = fields.Many2one(
        comodel_name='financial.cheque.movimento',
        string='Movimentação conta/caixa atual',
        compute='_compute_atual',
        store=True,
        index=True,
    )
    #state = fields.Selection(
        #selection=[
            #('novo', 'Novo'),
            #('recebido', 'Recebido'),
            #('depositado', 'Depositado'),
            #('repassado', 'Repassado'),
            #('devolvido_b', 'Devolvido pelo banco'),
            #('devolvido_p', 'Devolvido ao parceiro'),
        #],
        #string='Status',
        #default='novo',
    #)
    #
    # Observações
    #
    notes = fields.Text()
    #
    # Movimentações de Cheque
    #
    movimento_ids = fields.Many2many(
        comodel_name='financial.cheque.movimento',
        relation='financial_cheque_movimento_cheques',
        column1='cheque_id',
        column2='movimento_id',
        string='Movimentos',
    )
    #
    #
    # Movimentações Financeiras
    #
    financial_move_ids = fields.One2many(
        string='Pagamentos',
        comodel_name='financial.move',
        inverse_name='cheque_id',
        readonly=True,
    )

    @api.depends('participante_original_id', 'numero')
    def _compute_name(self):
        for record in self:
            if record.participante_original_id and record.numero:
                record.name = 'CHQ - ' + record.numero or '' + \
                            ' - ' + \
                            record.participante_original_id.display_name or ''

    @api.depends('partner_bank_id')
    def _compute_empresa_id(self):
        for record in self:
            if self.partner_bank_id:
                self.empresa_id = \
                    self.partner_bank_id.company_id.sped_empresa_id

    @api.depends('movimento_ids.data_confirmacao',
                 'movimento_ids.participante_origem_id',
                 'movimento_ids.participante_destino_id',
                 'movimento_ids.partner_bank_origem_id',
                 'movimento_ids.partner_bank_destino_id')
    def _compute_atual(self):
        for cheque in self:
            if not cheque.movimento_ids:
                continue

            movimento = cheque.movimento_ids[0]

            if movimento.participante_destino_id:
                cheque.participante_atual_id = \
                    movimento.participante_destino_id

                empresa = self.env['sped.empresa'].search(
                    [('participante_id', '=',
                    cheque.participante_atual_id.id)])

                if empresa:
                    cheque.empresa_atual_id = empresa

            else:
                cheque.participante_atual_id = False

            if movimento.partner_bank_destino_id:
                cheque.partner_bank_atual_id = \
                    movimento.partner_bank_destino_id

            else:
                cheque.partner_bank_atual_id = False

    @api.onchange('bank_id', 'agencia')
    def _onchange_municipio_id(self):
        for cheque in self:
            cheques = self.search([('bank_id', '=', cheque.bank_id.id),
                                   ('agencia', '=', cheque.agencia)])

            if len(cheques) > 0:
                cheque.municipio_id = cheques[0].municipio_id

    @api.onchange('codigo_barras')
    def onchange_codigo_barras(self):
        if self.codigo_barras and len(self.codigo_barras) >= 30:
            self.bank_id = self.env.get('res.bank').search([
                ('bic', '=', self.codigo_barras[:3])
            ])
            if not self.bank_id:
                raise UserError(_("Não foi encontrado banco com código %s")
                                % self.codigo_barras[:3])
            self.agencia = self.codigo_barras[3:7]
            self.numero = self.codigo_barras[11:17]
            self.conta = self.codigo_barras[22:-2] + '-' + \
                self.codigo_barras[-2]

    @api.onchange('participante_original_id')
    def onchange_participante_original_id(self):
        self.ensure_one()

        if not (self.titular_nome and self.titular_cnpj_cpf):
            self.titular_nome = self.participante_original_id.razao_social
            self.titular_cnpj_cpf = self.participante_original_id.cnpj_cpf

    def _valida_cnpj_cpf(self):
        self.ensure_one()

        if not self.titular_cnpj_cpf:
            return

        cnpj_cpf = limpa_formatacao(self.titular_cnpj_cpf or '')

        if not valida_cnpj(cnpj_cpf) and not valida_cpf(cnpj_cpf):
            raise ValidationError('CNPJ/CPF inválido')

        if len(cnpj_cpf) == 14:
            self.titular_cnpj_cpf = formata_cnpj(cnpj_cpf)
        else:
            self.titular_cnpj_cpf = formata_cpf(cnpj_cpf)

    #@api.constrains('titular_cnpj_cpf')
    #def constrains_cnpj_cpf(self):
        #for cheque in self:
            #cheque._valida_cnpj_cpf()

    @api.onchange('titular_cnpj_cpf')
    def onchange_cnpj_cpf(self):
        return self._valida_cnpj_cpf()

    #def mudar_estado(self, estado):
        #permitido = [
            #('novo', 'recebido'),
            #('recebido', 'depositado'),
            #('recebido', 'repassado'),
            #('recebido', 'devolvido_b'),
            #('depositado', 'devolvido_b'),
            #('devolvido_b', 'devolvido_p')
        #]
        #if (self.state, estado) in permitido:
            #self.state = estado
        #else:
            #raise UserError(_("Mudança do estado \"%s\" para estado \"%s\" "
                              #"não permitida.") % (self.state, estado))

    #def button_receber_cheque(self):
        #self.mudar_estado('recebido')

    #def button_depositar_cheque(self):
        #self.mudar_estado('depositado')

    #def button_repassar_cheque(self):
        #self.mudar_estado('repassado')

    #def button_devolver_cheque_banco(self):
        #self.mudar_estado('devolvido_b')

    #def button_devolver_cheque_parceiro(self):
        #self.mudar_estado('devolvido_p')

