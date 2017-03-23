# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    confirmed_orders = fields.Boolean(
        default=False
    )
    draft_invoices = fields.Boolean(
        default=False
    )
    sale_installed = fields.Boolean(
        compute='_is_sale_installed',
        store=False
    )

    @api.multi
    def _is_sale_installed(self):  # FIXME: função não é chamada
        ir_module = self.env['ir.module.module']
        res_found_module = ir_module.search_count([
            ('name', '=', 'sale'),
            ('state', '=', 'installed')])
        if res_found_module:
            for line in self:
                line.sale_installed = True
