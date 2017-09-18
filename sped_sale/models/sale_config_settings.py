# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_discount_global = fields.Selection([
        (0, 'Não permite desconto global no pedido de venda'),
        (1, 'Permite desconto global no pedido de venda')
        ], "Desconto Global",
        implied_group='sped_sale.group_discount_global')
    group_cumulative_discount_global = fields.Selection([
        (0, 'Não permite desconto cumulativo global no pedido de venda'),
        (1, 'Permite desconto cumulativo global no pedido de venda')
        ], "Desconto Global Cumulativo",
        implied_group='sped_sale.group_cumulative_discount_global')
