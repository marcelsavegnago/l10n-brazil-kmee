# -*- coding: utf-8 -*-
# Copyright (C) 2009  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    invoice_state = fields.Selection(
        [('2binvoiced', 'To be refunded/invoiced'),
         ('none', 'No invoicing')],
        default='2binvoiced',
    )

    @api.multi
    def create_returns(self):
        result = super(StockReturnPicking, self).create_returns()
        if self.sudo().mapped(
                'product_return_moves.move_id.picking_id.pos_order_ids'):
            # Create the return process if the product came from
            # a pos.order.

            picking_devolucao = self.assign_returning_picking(
                result)

            if picking_devolucao.state != u'confirmed':
                self.transfer_returning_picking(picking_devolucao)

            # Create the wizard that relate the source fiscal documents with
            # the generated picking
            current_session_ids = self.env['pos.session'].\
                search([('state', '!=', 'closed'),
                        ('user_id', '=', self._uid)])
            wizard_invoice = self.sudo().env['stock.invoice.onshipping'].\
                with_context(
                    active_ids=picking_devolucao.ids,
                    active_model='stock.picking',
                    company_id=picking_devolucao.company_id.id,
                ).create({})

            # Generate the returning invoice
            res_domain_invoice = wizard_invoice.open_invoice()

            picking_devolucao.invoice_id.company_id = \
                picking_devolucao.company_id

            # Confirm and send to SEFAZ the created returning invoice
            picking_devolucao.invoice_id.signal_workflow('invoice_validate')

            if current_session_ids[0].config_id.company_id != \
                    picking_devolucao.company_id:
                # Generate the transfer invoice
                invoice_transfer = \
                    self.create_transfer(picking_devolucao.invoice_id)
                res_domain_invoice['domain'] =\
                    [('id', '=', invoice_transfer.id)]
            user_id = str(self._uid)
            res_domain_invoice['context'].replace(user_id, '1', 1)

            return res_domain_invoice
        else:
            return result

    @api.multi
    def create_transfer(self, invoice):
        current_session_ids = self.env['pos.session']. \
            search([('state', '!=', 'closed'),
                    ('user_id', '=', self._uid)])
        config = current_session_ids[0].config_id
        result = super(StockReturnPicking, self).create_returns()
        if self.sudo().mapped(
                'product_return_moves.move_id.picking_id.pos_order_ids'):
            # Create the return process if the product came from
            # a pos.order.

            picking_devolucao = self.assign_returning_picking(
                result)
            picking_devolucao.partner_id = config.company_id.partner_id
            if picking_devolucao.state != u'confirmed':
                self.transfer_returning_picking(picking_devolucao)

            # Create the wizard that relate the source fiscal documents with
            # the generated picking

            posicao_fiscal = self.sudo().env['account.fiscal.position'].\
                search([('name', 'like', u'entre filiais - Envio'),
                        ('company_id', '=',
                         picking_devolucao.company_id.id)])[0]
            fiscal_category = self.env['l10n_br_account.fiscal.category'].\
                search([('code', '=', 'Envio de Transf.')])

            # Generate the returning invoice
            res_domain_invoice = invoice.copy_data()
            res_domain_invoice[0].update({
                'company_id': picking_devolucao.company_id.id,
                'nfe_purpose': u'1',
                'partner_id': config.company_id.partner_id.id,
                'fiscal_position': posicao_fiscal.id,
                'fiscal_category_id': fiscal_category.id,
                'partner_shipping_id': config.company_id.partner_id.id})
            invoice_transfer = self.sudo().env['account.invoice'].\
                create(res_domain_invoice[0])

            # Confirm and send to SEFAZ the created returning invoice
            invoice_transfer.signal_workflow('invoice_validate')
            return invoice_transfer

    def transfer_returning_picking(self, picking_devolucao):
        # Create and do the transfer in the return wizard
        wizard_transfer = picking_devolucao.do_enter_transfer_details()
        stock_transfer_details_obj = self.env['stock.transfer_details']
        wizard_transfer_id = stock_transfer_details_obj.with_context(
            active_ids=wizard_transfer['context']['active_ids'],
            active_model=wizard_transfer['context']['active_model']
        ).create({'picking_id': picking_devolucao.id})
        wizard_transfer_id.do_detailed_transfer()

    def assign_returning_picking(self, result):
        # Search and assign the returning picking
        result_domain = safe_eval(result['domain'])
        picking_ids = result_domain and result_domain[0] and \
                      result_domain[0][2]
        picking_devolucao = self.sudo().env['stock.picking'].browse(
            picking_ids)
        picking_devolucao.action_assign()
        return picking_devolucao
