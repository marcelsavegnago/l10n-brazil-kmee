# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATIDA LTDA
#   Aristides Caldeira <aristides.caldeira@kmee.com.br>
#   Daniel Sadamo <daniel.sadamo@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import division, print_function, unicode_literals

from openerp import api, fields, models


class SpedAccountMoveTemplate(models.Model):
    _name = b'sped.account.move.template'
    _description = 'Modelo de partidas dobradas'
    _rec_name = 'nome'

    nome = fields.Char(
        string='Descrição',
        required=True,
        index=True,
    )
    parent_id = fields.Many2one(
        comodel_name='sped.account.move.template',
        string='Modelo superior',
    )
    child_ids = fields.One2many(
        comodel_name='sped.account.move.template',
        inverse_name='parent_id',
        string='Modelos subordinados'
    )
    # operacao_ids = fields.Many2many(
    #     comodel_name='sped.operacao',
    #     relation='sped_account_move_template_operacao',
    #     column1='template_id',
    #     column2='operacao_id',
    #     string='Operações Fiscais',
    # )
    item_ids = fields.One2many(
        comodel_name='sped.account.move.template.item',
        inverse_name='template_id',
        string='Itens',
    )

    # @api.constrains('operacao_ids')
    # def _constraints_operacao_ids(self):
    #     for operacao in self.operacao_ids:
    #         if len(operacao.account_move_template_ids) > 1:
    #             raise UserError(u'A operação fiscal %s já tem um
    # modelo de partidas dobradas vinculado!' % operacao.nome)

    @api.multi
    def gera_account_move(self):
        for documento in self:
            dados = {
                'sped_documento_id': documento.id,
                'journal_id': documento.journal_id.id,
                'ref': documento.descricao,
                'sped_participante_id': documento.participante_id.id,
                'sped_empresa_id': documento.empresa_id.id,
                'partner_id': documento.participante_id.partner_id.id,
                'company_id': documento.empresa_id.company_id.id,
                'date': documento.data_entrada_saida,
            }

            if documento.account_move_id:
                if documento.account_move_id.state != 'draft':
                    # raise
                    continue
                account_move = documento.account_move_id
                account_move.write(dados)
            else:
                account_move = self.env['account.move'].create(dados)
                documento.account_move_id = account_move

            line_ids = [(5, 0, {})]

            documento.item_ids.gera_account_move_line(account_move,
                documento.account_move_template_id, line_ids)

            account_move.write({'line_ids': line_ids})
