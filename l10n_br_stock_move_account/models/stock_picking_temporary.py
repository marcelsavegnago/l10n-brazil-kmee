# -*- coding: utf-8 -*-
# Copyright (C) 2018  Luiz Felipe do Divino - ABGF - luiz.divino@abgf.gov.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


class StockPickingTemporary(models.Model):
    _name = 'stock.picking.temporary'

    stock_picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Transferência de Origem',
        required=True
    )

    account_move_id = fields.Many2one(
        comodel_name='account.move',
        string='Movimentação Transito Temporário',
    )

    line_ids = fields.One2many(
        comodel_name='stock.picking.temporary.line',
        inverse_name='stock_picking_temporary_id',
        string='Produtos',
    )


class StockPickingTemporaryLine(models.Model):
    _name = 'stock.picking.temporary.line'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Produto',
        required=True
    )

    quantidade = fields.Integer(
        string='Quantidade',
        required=True,
        default=0,
    )

    stock_picking_temporary_id = fields.Many2one(
        comodel_name='stock.picking.temporary',
        string='Movimentação temporária',
    )
