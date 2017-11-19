# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models, api


class SaleConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_dias_vencimento_cotacao = fields.Float(
        string="Dias de vencimento das cotações",
        default_model='sale.order.line',
        default=0.0,
    )
