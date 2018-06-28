# -*- coding: utf-8 -*-
# © 2018 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class FindPosOrder(models.TransientModel):
    _name = 'pos.order.find'

    name = fields.Char(
        string='Referência da Ordem',
    )

    @api.multi
    def search_order(self):
        orders = self.env['pos.order'].sudo().search(
            [('name', 'like', self.name)]
        )
        action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
        # for order in orders:
        #     order.sudo().write({'return_flag': True})
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif len(orders) == 1:
            action['views'] = [
                (self.env.ref('l10n_br_pos.view_pos_pos_form').id, 'form')]
            action['res_id'] = orders.ids[0]
        else:
            action = {'type': 'ir.actions.act_window'}
        action['context'] = {'default_return_flag': True}
        return action
