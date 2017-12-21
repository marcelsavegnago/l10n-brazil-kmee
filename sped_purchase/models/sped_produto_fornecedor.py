# -*- coding: utf-8 -*-
#
# Copyright 2017 Kmee Informática -
#   Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from odoo import api, fields, models, _
from odoo.addons.l10n_br_base.constante_tributaria import ORIGEM_MERCADORIA


class SpedProdutoFornecedor(models.Model):
    _name = b'sped.produto.fornecedor'

    produto_id = fields.Many2one(
        comodel_name='sped.produto',
        string='Produto no estoque',
    )

    codigo = fields.Char(
        string='Código do produto no fornecedor',
    )
    descricao_produto = fields.Char(
        string='Descrição do produto',
    )
    codigo_barras = fields.Char(
        string='Código de barras',
        size=14,
        index=True,
    )
    codigo_barras_tributacao = fields.Char(
        string='Código de barras para tributação comercial',
        size=14,
        index=True,
    )
    ncm_id = fields.Many2one(
        comodel_name='sped.ncm',
        string='NCM',
        required=True,
    )
    cest_id = fields.Many2one(
        comodel_name='sped.cest',
        string='CEST'
    )
    org_icms = fields.Selection(
        selection=ORIGEM_MERCADORIA,
        string='Origem da mercadoria',
        default='0'
    )
    preco = fields.Monetary(
        string='Preço',
    )
    fornecedor = fields.Many2one(
        comodel_name='sped.participante',
        string='Fornecedor',
        domain=[['eh_fornecedor', '=', True]],
    )
    estoque_em_maos = fields.Monetary(
        string='Estoque em mãos',
        currency_field='currency_unidade_id',
        compute='_compute_estoque',
    )
    currency_unidade_id = fields.Many2one(
        comodel_name='res.currency',
        string='Unidade',
    )
    
    documento_item_ids = fields.Many2one(
        comodel_name='sped.documento.item',
        inverse_name='produto_fornecedor',
        string='Item',
    )

    @api.depends('documento_item_ids.quantidade')
    def _compute_estoque(self):
        for produto_fornecedor in self:
            total = 0.0
            for item in produto_fornecedor.documento_item_ids:
                total += item.quantidade
            produto_fornecedor.estoque_em_maos = total
            total = 0.0
            valores = [
                (prod_for.estoque_em_maos, prod_for.currency_unidade_id)
                for prod_for in produto_fornecedor.produto_id.mapped(
                    'produto_fornecedor_ids')
            ]
            for valor, unidade in valores:
                total += valor
