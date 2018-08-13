# -*- coding: utf-8 -*-
# © 2018 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _


class FindPosOrder(models.TransientModel):
    _name = 'pos.order.find'

    state = fields.Selection(
        [('draft', 'Novo'),
         ('cancel', 'Cancelado'),
         ('paid', 'Pago'),
         ('done', 'Lançado'),
         ('invoiced', 'Faturado')],
        default='paid'
    )
    name = fields.Char(
        string='Referência da Ordem',
    )

    @api.multi
    def search_order(self):
        orders = self.env['pos.order'].sudo().search(
            [('name', 'like', self.name)]
        )
        action = \
            self.env.ref('l10n_br_pos.action_pos_find_order').read()[0]

        action['res_model'] = 'pos.find.order'
        action['target'] = 'current'
        action['type'] = 'ir.actions.act_window'
        action['context'] = self.env.context
        orders_found = []
        for order in orders:
            order.sudo()
            lines_ids = []
            vals = {
                'name': order.name,
                'order_id': order.id,
                'date_order': order.date_order,
                'session_id': order.session_id.id,
                'partner_id': order.partner_id.id,
                'chave_cfe': order.chave_cfe,
                'amount_total': order.amount_total,
                'canceled_order': order.canceled_order,
                'state': order.state,
            }
            order_find = self.env['pos.find.order']
            ord = order_find.create(vals)
            self._cr.commit()
            orders_found.append(ord.id)
            for line in order.lines:
                line.sudo()
                vals_l = {
                    'product_id': line.product_id.id,
                    'qty': line.qty,
                    'qtd_produtos_devolvidos': line.qtd_produtos_devolvidos,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'price_subtotal': line.price_subtotal,
                    'price_subtotal_incl': line.price_subtotal_incl,
                    'order_id': ord.id
                }
                self.env['pos.find.order.line'].create(vals_l)

        if len(orders_found) > 1:
            action['domain'] = [('id', 'in', orders_found)]
            action['view_type'] = 'tree'
            action['view_mode'] = 'tree'
            action['view_id'] = \
                (self.env.ref(
                    'l10n_br_pos.view_pos_find_order_tree').id, 'tree')

        elif len(orders_found) == 1:
            action['view_type'] = 'form'
            action['view_mode'] = 'form'
            action['view_id'] = [
                (self.env.ref(
                    'l10n_br_pos.view_find_order_form').id, 'form')]
            action['res_id'] = orders_found[0]
        else:
            raise Warning(_('Nenhum pedido encontrado!'))
        return action
