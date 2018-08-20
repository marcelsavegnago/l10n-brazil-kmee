# -*- coding: utf-8 -*-
# © 2016 KMEE INFORMATICA LTDA (https://kmee.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.tools.safe_eval import safe_eval


class StockPickingReturn(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields_list):
        res = super(StockPickingReturn, self.sudo()).default_get(fields_list)
        if self._context.get('order_id', False) == 'pos.find.order':
            res.update({'invoice_state': '2binvoiced'})
        return res

    @api.multi
    def _buscar_valor_total_devolucao(self, pos_order):
        precos_produtos_pos_order = {}
        for line in pos_order.lines:
            precos_produtos_pos_order.update({
                line.product_id.id: line.price_unit - (
                    line.price_unit * (line.discount/100)
                )
            })
        valor_total_devolucao = 0.00
        for line in self.product_return_moves:
            valor_total_devolucao += \
                precos_produtos_pos_order[line.product_id.id] * line.quantity

        return valor_total_devolucao

    @api.multi
    def create_returns(self):
        if self.env.context.get('pos_order_id'):
            pos_order = self.env['pos.find.order'].browse(
                self.env.context['pos_order_id']
            )
            for product_line in self.product_return_moves:
                for line in pos_order.lines:
                    if line.product_id == product_line.product_id:
                        if line.qtd_produtos_devolvidos + \
                                product_line.quantity > line.qty:
                            raise Warning(
                                _('Esta quantidade do produto %s não pode '
                                  'ser devolvida') %
                                (line.product_id.display_name))

            res = super(StockPickingReturn, self.sudo()).create_returns()
            result_domain = safe_eval(res['domain'])
            picking_ids = result_domain and result_domain[0] and \
                          result_domain[0][2]
            picking_devolucao = self.sudo().env['stock.picking'].browse(
                picking_ids)
            cat_fiscal_devolucao = picking_devolucao.fiscal_category_id
            obj_fp_rule = self.sudo().env['account.fiscal.position.rule']
            current_session_ids = self.env['pos.session']. \
                search([('state', '!=', 'closed'),
                        ('user_id', '=', self._uid)])
            kwargs = {
                'partner_id':
                    current_session_ids[0].config_id.company_id.partner_id.id,
                'partner_shipping_id':
                    current_session_ids[0].config_id.company_id.partner_id.id,
                'fiscal_category_id': cat_fiscal_devolucao.id,
                'company_id': current_session_ids[0].config_id.company_id.id,
            }
            picking_devolucao.fiscal_position = \
                obj_fp_rule.apply_fiscal_mapping({'value': {}}, **kwargs
                                                )['value']['fiscal_position']

            picking_devolucao.company_id = \
                current_session_ids[0].config_id.company_id.id

            valor_total_devolucao = self._buscar_valor_total_devolucao(
                pos_order
            )
            partner_id = pos_order.partner_id or self.env['res.partner'].\
                browse(self._context['partner_id'])
            partner_id.credit_limit += valor_total_devolucao
            return res

        return super(StockPickingReturn, self.sudo()).create_returns()


class PorOrderReturn(models.TransientModel):
    _name = 'pos.order.return'
    _description = "Pos Order Return"

    @api.model
    def _get_partner(self):
        partner = self._context.get('partner_id', False)
        if partner:
            return partner

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=u"Cliente",
        help=u"Selecione ou Defina um novo cliente para efetuar a devoluçao",
        default=_get_partner,
        required=True
    )

    @staticmethod
    def _check_picking_parameters(order, uid):
        current_session_ids = order.env['pos.session']. \
            search([('state', '!=', 'closed'), ('user_id', '=', uid)])
        config_id = current_session_ids[0].config_id
        if not order.picking_id.fiscal_category_id:
            # Picking id not set
            order.picking_id.fiscal_category_id = (
                config_id.out_pos_fiscal_category_id or
                config_id.company_id.out_pos_fiscal_category_id)
        if not order.picking_id.fiscal_category_id.refund_fiscal_category_id:
            order.picking_id.fiscal_category_id.refund_fiscal_category_id = (
                config_id.refund_pos_fiscal_category_id or
                config_id.company_id.refund_pos_fiscal_category_id)
        order.picking_id.partner_id = order.partner_id
        return True

    @api.multi
    def create_returns(self):
        self.ensure_one()
        if self.env.context.get("order_id", None):
            order_id = \
                self.env['pos.find.order'].browse(self._context['order_id'])
        else:
            order_id = self.env.context.get("active_ids")
        order_find = self.env['pos.find.order'].browse(order_id)

        order = order_find.order_id
        order.sudo().partner_id = self.partner_id
        self._check_picking_parameters(order.sudo(), self._uid)

        ctx = dict(self._context)
        ctx['pos_order_id'] = order_id
        ctx['active_ids'] = order.sudo().picking_id.ids
        ctx['active_id'] = order.sudo().picking_id.id
        ctx['contact_display'] = 'partner_address'
        ctx['search_disable_custom_filters'] = True
        ctx['partner_id'] = self.partner_id.id

        form = self.env.ref('stock.view_stock_return_picking_form', False)
        self.sudo()
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.return.picking',
            'views': [(form.id, 'form')],
            'target': 'new',
            'context': ctx,
        }
