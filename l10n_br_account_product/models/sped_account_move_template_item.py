# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATIDA LTDA
#   Aristides Caldeira <aristides.caldeira@kmee.com.br>
#   Daniel Sadamo <daniel.sadamo@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import division, print_function, unicode_literals

from openerp import api, fields, models
from ..constantes import (
    CAMPO_DOCUMENTO_FISCAL,
    CAMPO_DOCUMENTO_FISCAL_ITEM,
)


class SpedAccountMoveTemplateItem(models.Model):
    _name = b'sped.account.move.template.item'
    _description = 'Item do modelo de partidas dobradas'

    template_id = fields.Many2one(
        comodel_name='sped.account.move.template',
        string='Modelo',
        required=True,
        ondelete='cascade',
    )
    campo = fields.Selection(
        selection=CAMPO_DOCUMENTO_FISCAL,
        string='Campo',
        required=True,
    )
    account_debito_id = fields.Many2one(
        comodel_name='account.account',
        string='Débito',
        domain=[('type', '!=', 'view')],
    )
    account_credito_id = fields.Many2one(
        comodel_name='account.account',
        string='Crédito',
        domain=[('type', '!=', 'view')],
    )

    @api.multi
    def gera_account_move_line(self, account_move, move_template, line_ids,
                               campos_jah_contabilizados=[]):
        for item in self:
            for template_item in move_template.item_ids:
                if not getattr(item, template_item.campo, False):
                    continue

                if template_item.campo in campos_jah_contabilizados:
                    continue

                #
                # Nas notas de entrada por compra ou devolução de venda, se
                # não se vai aproveitar o crédito do imposto, ele não é
                # contabilizado à parte
                #
                if item.documento_id.eh_compra or \
                        item.documento_id.eh_devolucao_venda:
                    if template_item.campo in ('vr_icms', 'vr_icms_sn') and \
                            not item.credita_icms:
                        continue
                    elif template_item.campo == 'vr_icms_st' and \
                            not item.credita_icms_st:
                        continue
                    elif template_item.campo == 'vr_ipi' and \
                            not item.credita_ipi:
                        continue
                    elif template_item.campo in ('vr_pis_proprio',
                        'vr_cofins_proprio') and not item.credita_pis_cofins:
                        continue

                valor = getattr(item, template_item.campo, 0)

                if not valor:
                    continue

                dados = {
                    'move_id': account_move.id,
                    'sped_documento_item_id': item.id,
                    'name': item.produto_id.nome,
                    'narration': template_item.campo,
                    'debit': valor,
                    'currency_id': item.currency_id.id,
                }

                account_debito = None
                if template_item.account_debito_id:
                    account_debito = template_item.account_debito_id
                elif template_item.campo in CAMPO_DOCUMENTO_FISCAL_ITEM:
                    product = item.produto_id.product_id
                    if item.documento_id.eh_venda:
                        account_debito = product.property_account_income_id
                    elif item.documento_id.eh_compra:
                        account_debito = product.property_account_expense_id
                else:
                    partner = item.documento_id.participante_id.partner_id
                    if item.documento_id.eh_venda:
                        account_debito = \
                            partner.property_account_receivable_id
                    elif item.documento_id.eh_compra:
                        account_debito = partner.property_account_payable_id

                if account_debito is None:
                    # raise
                    pass
                else:
                    dados['account_id'] = account_debito.id

                line_ids.append([0, 0, dados])

                dados = {
                    'move_id': account_move.id,
                    'sped_documento_item_id': item.id,
                    'name': item.produto_id.nome,
                    'narration': template_item.campo,
                    'credit': valor,
                    'currency_id': item.currency_id.id,
                }

                account_credito = None
                if template_item.account_credito_id:
                    account_credito = template_item.account_credito_id
                elif template_item.campo in CAMPO_DOCUMENTO_FISCAL_ITEM:
                    product = item.produto_id.product_id
                    if item.documento_id.eh_venda:
                        account_credito = product.property_account_income_id
                    elif item.documento_id.eh_compra:
                        account_credito = product.property_account_expense_id
                else:
                    partner = item.documento_id.participante_id.partner_id
                    if item.documento_id.eh_venda:
                        account_credito = \
                            partner.property_account_receivable_id
                    elif item.documento_id.eh_compra:
                        account_credito = partner.property_account_payable_id

                if account_credito is None:
                    # raise
                    pass
                else:
                    dados['account_id'] = account_credito.id

                line_ids.append([0, 0, dados])
                campos_jah_contabilizados.append(template_item.campo)

        if move_template.parent_id:
            self.gera_account_move_line(
                account_move, move_template.parent_id,
                line_ids, campos_jah_contabilizados=campos_jah_contabilizados)
