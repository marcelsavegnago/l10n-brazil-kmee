# -*- coding: utf-8 -*-
#
# Copyright 2017 Kmee Informática -
#   Gabriel Cardoso de Faria <gabriel.cardoso@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from odoo import api, fields, models, _


class SpedProduto(models.Model):
    _inherit = b'sped.produto'

    produto_fornecedor_ids = fields.One2many(
        comodel_name='sped.produto.fornecedor',
        string='Produtos de fornecedor',
        inverse_name='produto_id',
    )
