# -*- coding: utf-8 -*-
# Copyright (C) 2018  Luiz Felipe do Divino - ABGF - luiz.divino@abgf.gov.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    account_move_ids = fields.One2many(
        string='Movimentações Contábeis',
        comodel_name='account.move',
        inverse_name='picking_id',
    )

    @api.multi
    def action_provisorio(self):
        self.env.cr.execute("update stock_picking set state='provisorio'"
                            "where id=%d" % self.id)
        return True

    @api.depends('code', 'state')
    def get_status(self):
        is_draft = False
        is_incoming = False
        is_done = False

        if self.state == 'draft':
            is_draft = True
        elif self.state == 'provisorio':
            is_done = True
        if self.code == 'incoming':
            is_incoming = True
        self.status = (is_incoming and not is_done) or \
                      (is_draft and not is_incoming)
