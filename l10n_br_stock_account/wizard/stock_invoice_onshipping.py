# -*- coding: utf-8 -*-
# Copyright (C) 2009  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import ast

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError

FISCAL_DOC_REF = [
    ('account.invoice', u'Fatura'),
]


class StockInvoiceOnShipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def _fiscal_doc_ref_selection(self):
        return FISCAL_DOC_REF

    @api.multi
    def _compute_fiscal_doc_ref(self):
        """
        Delegate calculation of fiscal_doc_ref default.

        A string argument to fields.Reference(default=...) is interpreted as
        the actual default value instead of method to look up the default.

        Here we delegate to self._fiscal_doc_ref_default() so inheriting models
        can override it.
        """
        return self._fiscal_doc_ref_default()

    def active_picking_ids(self):
        context = self.env.context
        return self.env['stock.picking'].browse(context.get('active_ids'))

    @api.model
    def get_returned_picking_ids(self):
        return self.active_picking_ids().mapped(
            'move_lines.origin_returned_move_id.picking_id'
        )

    @api.multi
    def _fiscal_doc_ref_default(self):
        return_picking_ids = self.get_returned_picking_ids()
        ref_id = return_picking_ids.mapped('invoice_ids')[:1].id
        res = 'account.invoice,%d' % ref_id
        return res

    journal_id = fields.Many2one(
        'account.journal', 'Destination Journal',
        domain="[('type', '=', journal_type)]")
    fiscal_category_journal = fields.Boolean(
        u'Diário da Categoria Fiscal', default=True)

    fiscal_doc_ref = fields.Reference(selection="_fiscal_doc_ref_selection",
                                      readonly=False,
                                      default=_compute_fiscal_doc_ref,
                                      string=u'Documento Fiscal Relacionado')

    @api.multi
    def open_invoice(self):
        context = dict(self.env.context)
        for wizard in self:
            fiscal_document_code = (wizard.journal_id.company_id.
                                    product_invoice_id.code)
            context.update(
                {'fiscal_document_code': fiscal_document_code})
        result = super(StockInvoiceOnShipping,
                       self.with_context(context)).open_invoice()
        if result.get('context'):
            super_context = ast.literal_eval(result.get('context'))
            super_context.update(context)
            result['context'] = str(super_context)
        return result

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        context = dict(self.env.context)

        picking = self.active_picking_ids()
        #
        # Permite o faturamento com usuário de outra empresa, desde que o mesmo
        # tenha acesso a outra empresa, mas no momento não esteja logado com
        # a empresa do picking.
        #
        context['force_company'] = picking.company_id.id

        journal_id = picking.with_context(
            context).fiscal_category_id.property_journal
        fiscal_document_code = picking.company_id.product_invoice_id.code
        context.update(
            {'fiscal_document_code': fiscal_document_code})
        if self.fiscal_doc_ref:
            context.update({'fiscal_doc_ref': self.fiscal_doc_ref})
        if not journal_id:
            raise UserError(
                _('Invalid Journal!'),
                _('There is not journal defined for this company: %s in '
                  'fiscal operation: %s !') %
                (picking.company_id.name,
                 picking.fiscal_category_id.name))
        self.write({'journal_id': journal_id.id})

        result = super(StockInvoiceOnShipping,
                       self.with_context(context)).create_invoice()
        return result
