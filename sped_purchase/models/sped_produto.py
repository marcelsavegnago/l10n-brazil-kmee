# -*- coding: utf-8 -*-
#
# Copyright 2017 Kmee Informática -
#   Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from odoo import api, fields, models, _


class SpedProduto(models.Model):
    _inherit = b'sped.produto'

    parent_id = fields.Many2one(
        comodel_name='sped.produto',
        string='Produto no estoque',
    )

    child_ids = fields.One2many(
        comodel_name='sped.produto',
        string='Produtos de fornecedor',
        inverse_name='parent_id',
    )

    tipo_produto = fields.Selection(
        selection=[
            ('fornecedor', 'Produto de fornecedor'),
            ('estoque', 'Produto no estoque'),
        ],
        string='Tipo de produto:',
    )
