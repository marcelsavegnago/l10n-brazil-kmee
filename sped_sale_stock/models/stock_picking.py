# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        super(StockPicking, self).do_transfer()
        for picking in self:
            if picking.sale_id:
                picking.operacao_id = picking.sale_id.operacao_produto_id.id
                documento = picking.gera_documento()
                if documento:
                    picking.documento_ids |= documento

    @api.model
    def create(self, vals):
        pickings = super(StockPicking, self).create(vals)
        for picking in pickings:
            if picking.sale_id:
                picking.operacao_id = picking.operacao_produto_id.id
