# -*- coding: utf-8 -*-
# Copyright (C) 2018  Luiz Felipe do Divino - ABGF - luiz.divino@abgf.gov.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime
from openerp import models, fields, api, _


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.one
    def do_detailed_transfer_core(self):
        if self.picking_id.state not in \
                ['assigned', 'partially_available', 'provisorio']:
            raise Warning(_(
                'You cannot transfer a picking in state \'%s\'.'
            ) % self.picking_id.state)

        processed_ids = []
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            for prod in lstits:
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': prod.lot_id.id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.with_context(no_recompute=True).write(
                        pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    packop_id = self.env['stock.pack.operation'].create(
                        pack_datas)
                    processed_ids.append(packop_id.id)
        # Delete the others
        packops = self.env['stock.pack.operation'].search(
            ['&', ('picking_id', '=', self.picking_id.id), '!',
             ('id', 'in', processed_ids)])
        packops.unlink()

        # Execute the transfer of the picking
        self.picking_id.do_transfer()

        return True


    @api.multi
    def do_detailed_transfer(self):
        self.do_detailed_transfer_core()

        if self.picking_id.company_id.active_stock_move_account:
            self.picking_id.gerar_lancamento_recebimento_definitivo()

        return True
