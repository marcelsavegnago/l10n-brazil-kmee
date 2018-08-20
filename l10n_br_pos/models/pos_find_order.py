# -*- coding: utf-8 -*-
# © 2016 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class PosFindOrder(models.TransientModel):
    _name = 'pos.find.order'

    order_id = fields.Many2one(
        comodel_name='pos.order'
    )
    name = fields.Char()
    date_order = fields.Datetime()
    session_id = fields.Many2one(
        comodel_name='pos.session',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
    )
    chave_cfe = fields.Char()
    lines = fields.One2many(
        comodel_name='pos.find.order.line',
        inverse_name='order_id',
    )
    amount_total = fields.Float()
    canceled_order = fields.Boolean()
    state = fields.Selection(
        [
            ('draft', 'Novo'),
            ('paid', 'Pago'),
            ('cancel', 'Cancelado'),
            ('done', 'Lançado'),
            ('invoiced', 'Faturado')
        ],
        default='paid'
    )
    create_uid = fields.Many2one(
        comodel_name='res.users',
        default=lambda self: self.env.user.id
    )

    @api.model
    def create(self, vals):
        result = super(PosFindOrder, self).create(vals)
        result.create_uid = self.env.user
        return result


class PosFindOrderLine(models.TransientModel):
    _name = 'pos.find.order.line'

    product_id = fields.Many2one(
        comodel_name='product.product'
    )
    qty = fields.Float()
    qtd_produtos_devolvidos = fields.Integer()
    price_unit = fields.Float()
    discount = fields.Float()
    price_subtotal = fields.Float()
    price_subtotal_incl = fields.Float()
    order_id = fields.Many2one(
        comodel_name='pos.find.order',
    )
