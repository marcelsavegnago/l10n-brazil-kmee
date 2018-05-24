# -*- coding: utf-8 -*-
# Copyright (C) 2018  Luiz Felipe do Divino - ABGF - luiz.divino@abgf.gov.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, fields, models


STATE = [
    ('draft', 'Rascunho'),
    ('cancel', 'Cancelado'),
    ('waiting', 'Esperando outra operação'),
    ('confirmed', 'Aguardando disponibilidade'),
    ('partially_available', 'Parcialmente Disponível'),
    ('provisorio', 'Recebimento Provisório'),
    ('assigned', 'Aguardando recebimento'),
    ('done', 'Recebido'),
]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(
        help="",
        selection=STATE,
    )
    code = fields.Selection(
        related='picking_type_id.code',
        store=True,
    )
    status = fields.Boolean(
        compute='get_status',
    )

    temporary_received_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diário Recebimento Provisório'
    )

    temporary_received_ids = fields.One2many(
        comodel_name='stock.picking.temporary',
        inverse_name='stock_picking_id',
        string='Recebimentos Provisórios'
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
