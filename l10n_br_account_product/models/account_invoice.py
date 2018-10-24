# -*- coding: utf-8 -*-
# Copyright (C) 2013  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import datetime

from odoo import models, fields, api, _, tools
from odoo.addons import decimal_precision as dp
from odoo.exceptions import (RedirectWarning,
                             ValidationError,
                             Warning as UserError)

from .l10n_br_account_product import (
    PRODUCT_FISCAL_TYPE,
    PRODUCT_FISCAL_TYPE_DEFAULT)

from .product_template import PRODUCT_ORIGIN
from odoo.addons.l10n_br_account_product.sped.nfe.validator import txt


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _order = 'date_hour_invoice DESC, internal_number DESC'

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount',
                 'currency_id', 'company_id', 'date_invoice', 'type',
                 'account_payment_ids.amount')
    def _compute_amount(self):
        self.icms_base = 0.0
        self.icms_base_other = 0.0
        self.icms_value = 0.0
        self.icms_st_base = 0.0
        self.icms_st_value = 0.0
        self.ipi_base = sum(line.ipi_base for line in self.invoice_line_ids)
        self.ipi_base_other = sum(
            line.ipi_base_other for line in self.invoice_line_ids)
        self.ipi_value = sum(line.ipi_value for line in self.invoice_line_ids)
        self.pis_base = sum(line.pis_base for line in self.invoice_line_ids)
        self.pis_value = sum(line.pis_value for line in self.invoice_line_ids)
        self.cofins_base = sum(
            line.cofins_base for line in self.invoice_line_ids)
        self.cofins_value = sum(
            line.cofins_value for line in self.invoice_line_ids)
        self.ii_value = sum(line.ii_value for line in self.invoice_line_ids)
        self.icms_fcp_value = sum(
            line.icms_fcp_value for line in self.invoice_line_ids)
        self.icms_dest_value = sum(
            line.icms_dest_value for line in self.invoice_line_ids)
        self.icms_origin_value = sum(
            line.icms_origin_value for line in self.invoice_line_ids)
        self.amount_discount = sum(
            line.discount_value for line in self.invoice_line_ids)
        self.amount_insurance = sum(
            line.insurance_value for line in self.invoice_line_ids)
        self.amount_costs = sum(
            line.other_costs_value for line in self.invoice_line_ids)
        self.amount_freight = sum(
            line.freight_value for line in self.invoice_line_ids)
        self.amount_total_taxes = sum(
            line.total_taxes for line in self.invoice_line_ids)
        self.amount_gross = sum(
            line.price_gross for line in self.invoice_line_ids)
        self.amount_tax_discount = 0.0
        self.amount_untaxed = sum(
            line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(tax.amount
                              for tax in self.tax_line_ids
                              if not tax.tax_id.tax_group_id.tax_discount)
        self.amount_total = self.amount_tax + self.amount_untaxed

        for line in self.invoice_line_ids:
            if line.icms_cst_id.code not in (
                    '101', '102', '201', '202', '300', '500'):
                self.icms_base += line.icms_base
                self.icms_base_other += line.icms_base_other
                self.icms_value += line.icms_value
            else:
                self.icms_base += 0.00
                self.icms_base_other += 0.00
                self.icms_value += 0.00
            self.icms_st_base += line.icms_st_base
            self.icms_st_value += line.icms_st_value

        # Calculando o grupo fatura
        self.amount_payment_original = sum(
            p.amount_original for p in self.account_payment_line_ids)
        self.amount_payment_discount = sum(
            p.amount_discount for p in self.account_payment_line_ids)
        self.amount_payment_net = sum(
            p.amount_net for p in self.account_payment_line_ids)

        # Calculando o troco
        if self.amount_payment_net:
            self.amount_change = self.amount_payment_net - self.amount_total

    @api.model
    @api.returns('l10n_br_account.fiscal_category')
    def _default_fiscal_category(self):
        DEFAULT_FCATEGORY_PRODUCT = {
            'in_invoice': 'in_invoice_fiscal_category_id',
            'out_invoice': 'out_invoice_fiscal_category_id',
            'in_refund': 'in_refund_fiscal_category_id',
            'out_refund': 'out_refund_fiscal_category_id'
        }
        default_fo_category = {'product': DEFAULT_FCATEGORY_PRODUCT}
        invoice_type = self._context.get('type', 'out_invoice')
        invoice_fiscal_type = self._context.get('fiscal_type', 'product')
        company = self.env['res.company'].browse(self.env.user.company_id.id)
        return company[default_fo_category[invoice_fiscal_type][invoice_type]]

    @api.model
    def _default_fiscal_document(self):
        if self.env.context.get('fiscal_document_code'):
            company = self.env['res.company'].browse(
                self.env.user.company_id.id)
            return company.product_invoice_id

    @api.model
    def _default_nfe_version(self):
        if self.env.context.get('fiscal_document_code'):
            company = self.env['res.company'].browse(
                self.env.user.company_id.id)
            return company.nfe_version

    @api.model
    def _default_fiscal_document_serie(self):
        result = self.env['l10n_br_account.document.serie']
        if self.env.context.get('fiscal_document_code'):
            company = self.env['res.company'].browse(
                self.env.user.company_id.id)
            fiscal_document_series = [doc_serie for doc_serie in
                                      company.document_serie_product_ids if
                                      doc_serie.fiscal_document_id.id ==
                                      company.product_invoice_id.id and
                                      doc_serie.active]
            if fiscal_document_series:
                result = fiscal_document_series[0]
        return result

    @api.model
    def _default_nfe_purpose(self):
        nfe_purpose_default = {
            'in_invoice': '1',
            'out_invoice': '1',
            'in_refund': '4',
            'out_refund': '4'
        }
        invoice_type = self.env.context.get('type', 'out_invoice')
        return nfe_purpose_default.get(invoice_type)

    @api.one
    @api.depends('invoice_line_ids.cfop_id')
    def _compute_cfops(self):
        lines = self.env['l10n_br_account_product.cfop']
        for line in self.invoice_line_ids:
            if line.cfop_id:
                lines |= line.cfop_id
        self.cfop_ids = (lines).sorted()

    issuer = fields.Selection(
        [('0', u'Emissão própria'), ('1', 'Terceiros')],
        'Emitente',
        default='0',
        readonly=True,
        states={'draft': [('readonly', False)]})

    # FIXME
    internal_number = fields.Char(
        string='Invoice Number',
        size=32,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="""Unique number of the invoice, computed
            automatically when the invoice is created.""")

    type = fields.Selection(
        states={'draft': [('readonly', False)]})

    vendor_serie = fields.Char(
        string=u'Série NF Entrada',
        size=12,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help=u"Série do número da Nota Fiscal do Fornecedor")

    nfe_version = fields.Selection(
        selection=[('1.10', '1.10'),
                   ('2.00', '2.00'),
                   ('3.10', '3.10'),
                   ('4.00', '4.00')],
        string=u'Versão NFe',
        readonly=True,
        default=_default_nfe_version,
        states={'draft': [('readonly', False)]})

    date_hour_invoice = fields.Datetime(
        string=u'Data e hora de emissão',
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
        help="Deixe em branco para usar a data atual")

    ind_final = fields.Selection(
        selection=[('0', u'Não'),
                   ('1', u'Sim')],
        string=u'Consumidor final',
        readonly=True,
        related='fiscal_position_id.ind_final',
        states={'draft': [('readonly', False)]},
        required=False,
        help=u'Indica operação com Consumidor final.')

    ind_pres = fields.Selection(
        selection=[('0', u'Não se aplica (por exemplo,'
                         u' Nota Fiscal complementar ou de ajuste)'),
                   ('1', u'Operação presencial'),
                   ('2', u'Operação não presencial, pela Internet'),
                   ('3', u'Operação não presencial, Teleatendimento'),
                   ('4', u'NFC-e em operação com entrega em domicílio'),
                   ('5', u'Operação presencial, fora do estabelecimento'),
                   ('9', u'Operação não presencial, outros')],
        string=u'Tipo de operação',
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=False,
        default='0',
        help=u'Indicador de presença do comprador no\n'
             u'estabelecimento comercial no momento\n'
             u'da operação.',)

    fiscal_document_id = fields.Many2one(
        comodel_name='l10n_br_account.fiscal.document',
        string=u'Documento',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_fiscal_document)

    fiscal_document_electronic = fields.Boolean(
        related='fiscal_document_id.electronic')

    document_serie_id = fields.Many2one(
        comodel_name='l10n_br_account.document.serie',
        string=u'Série',
        domain="[('fiscal_document_id', '=', fiscal_document_id),\
            ('company_id','=',company_id)]",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_fiscal_document_serie)

    fiscal_category_id = fields.Many2one(
        comodel_name='l10n_br_account.fiscal.category',
        string=u'Categoria Fiscal',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_fiscal_category)

    date_in_out = fields.Datetime(
        string=u'Data de Entrada/Saida',
        readonly=True,
        states={'draft': [('readonly', False)]},
        index=True,
        copy=False,
        help="Deixe em branco para usar a data atual")

    fiscal_type = fields.Selection(
        selection=PRODUCT_FISCAL_TYPE,
        string=u'Tipo Fiscal',
        default=PRODUCT_FISCAL_TYPE_DEFAULT)

    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Endereço de Entrega',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Shipping address for current sales order.")

    shipping_state_id = fields.Many2one(
        comodel_name='res.country.state',
        string=u'Estado de Embarque')

    shipping_location = fields.Char(
        string=u'Local de Embarque',
        size=32)

    expedition_location = fields.Char(
        string='Local de Despacho',
        size=32)

    nfe_purpose = fields.Selection(
        selection=[('1', 'Normal'),
                   ('2', 'Complementar'),
                   ('3', 'Ajuste'),
                   ('4', u'Devolução de Mercadoria')],
        string=u'Finalidade da Emissão',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_default_nfe_purpose)

    nfe_access_key = fields.Char(
        string=u'Chave de Acesso NFE',
        size=44,
        readonly=True, states={'draft': [('readonly', False)]},
        copy=False)

    nfe_protocol_number = fields.Char(
        string=u'Protocolo',
        size=15,
        readonly=True,
        copy=False, states={'draft': [('readonly', False)]})

    nfe_status = fields.Char(
        string=u'Status na Sefaz',
        size=44,
        readonly=True,
        copy=False)

    nfe_date = fields.Datetime(
        string=u'Data do Status NFE',
        readonly=True,
       copy=False)

    nfe_export_date = fields.Datetime(
        string=u'Exportação NFE',
        readonly=True)

    cfop_ids = fields.Many2many(
        comodel_name='l10n_br_account_product.cfop',
        string=u'CFOP',
        copy=False,
        compute='_compute_cfops')

    fiscal_document_related_ids = fields.One2many(
        comodel_name='l10n_br_account_product.document.related',
        inverse_name='invoice_id',
        string=u'Fiscal Document Related',
        readonly=True,
        states={'draft': [('readonly', False)]})

    carrier_name = fields.Char(
        string=u'Nome Transportadora',
        size=32)

    vehicle_plate = fields.Char(
        string=u'Placa do Veículo',
        size=7)

    vehicle_state_id = fields.Many2one(
        comodel_name='res.country.state',
        string=u'UF da Placa')

    vehicle_l10n_br_city_id = fields.Many2one(
        comodel_name='l10n_br_base.city',
        string=u'Município',
        domain="[('state_id', '=', vehicle_state_id)]")

    amount_untaxed = fields.Float(
        string=u'Untaxed',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_tax = fields.Float(
        string=u'Tax',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_total = fields.Float(
        string=u'Total',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_gross = fields.Float(
        string=u'Vlr. Bruto',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    amount_discount = fields.Float(
        string=u'Desconto',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    icms_base = fields.Float(
        string=u'Base ICMS',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    icms_base_other = fields.Float(
        string=u'Base ICMS Outras',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    icms_value = fields.Float(
        string=u'Valor ICMS',
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        store=True)

    icms_st_base = fields.Float(
        string=u'Base ICMS ST',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    icms_st_value = fields.Float(
        string=u'Valor ICMS ST',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    ipi_base = fields.Float(
        string=u'Base IPI',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    ipi_base_other = fields.Float(
        string=u'Base IPI Outras',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    ipi_value = fields.Float(
        string=u'Valor IPI',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    pis_base = fields.Float(
        string=u'Base PIS',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    pis_value = fields.Float(
        string=u'Valor PIS',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    cofins_base = fields.Float(
        string=u'Base COFINS',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    cofins_value = fields.Float(
        string=u'Valor COFINS',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    ii_value = fields.Float(
        string=u'Valor II',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    icms_fcp_value = fields.Float(
        string=u'Valor total do Fundo de Combate à Pobreza (FCP)',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    icms_dest_value = fields.Float(
        string=u'Valor total do ICMS Interestadual para a UF de destino',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    icms_origin_value = fields.Float(
        string=u'Valor total do ICMS Interestadual para a UF do remetente',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        readonly=True)

    weight = fields.Float(
        string=u'Gross weight',
        states={'draft': [('readonly', False)]},
        help="The gross weight in Kg.",
        readonly=True)

    weight_net = fields.Float(
        string=u'Net weight',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="The net weight in Kg.")

    number_of_packages = fields.Integer(
        string=u'Volume',
        readonly=True,
        states={'draft': [('readonly', False)]})

    kind_of_packages = fields.Char(
        string=u'Espécie',
        size=60,
        readonly=True,
        states={'draft': [('readonly', False)]})

    brand_of_packages = fields.Char(
        string=u'Brand',
        size=60,
        readonly=True,
        states={'draft': [('readonly', False)]})

    notation_of_packages = fields.Char(
        string=u'Numeração',
        size=60,
        readonly=True,
        states={'draft': [('readonly', False)]})

    amount_insurance = fields.Float(
        string=u'Valor do Seguro',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_freight = fields.Float(
        string=u'Valor do Frete',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_costs = fields.Float(
        string=u'Outros Custos',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_total_taxes = fields.Float(
        string=u'Total de Tributos',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    amount_change = fields.Float(
        string='Troco',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount')

    account_payment_ids = fields.One2many(
        string='Dados de Pagamento',
        comodel_name='account.invoice.payment',
        inverse_name='invoice_id',
    )
    account_payment_line_ids = fields.One2many(
        string='Dados da cobrança',
        comodel_name='account.invoice.payment.line',
        inverse_name='invoice_id',
    )
    amount_payment_original = fields.Float(
        string='Vr Original',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        help='vOrig'
    )
    amount_payment_discount = fields.Float(
        string='Vr Desconto',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        help='vDesc',
    )
    amount_payment_net = fields.Float(
        string='Vr Liquido',
        store=True,
        digits=dp.get_precision('Account'),
        compute='_compute_amount',
        help='vLiq',
    )

    @api.one
    @api.constrains('number')
    def _check_invoice_number(self):
        domain = []
        if self.number:
            fiscal_document = self.fiscal_document_id and\
                self.fiscal_document_id.id or False
            domain.extend([('internal_number', '=', self.number),
                           ('fiscal_type', '=', self.fiscal_type),
                           ('fiscal_document_id', '=', fiscal_document)
                           ])
            if self.issuer == '0':
                domain.extend([
                    ('company_id', '=', self.company_id.id),
                    ('internal_number', '=', self.number),
                    ('fiscal_document_id', '=', self.fiscal_document_id.id),
                    ('issuer', '=', '0')])
            else:
                domain.extend([
                    ('partner_id', '=', self.partner_id.id),
                    ('vendor_serie', '=', self.vendor_serie),
                    ('issuer', '=', '1')])

            invoices = self.env['account.invoice'].search(domain)
            if len(invoices) > 1:
                raise UserError(u'Não é possível registrar documentos\
                              fiscais com números repetidos.')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        context = self.env.context
        fiscal_document_code = context.get('fiscal_document_code')
        active_id = context.get('active_id')
        nfe_form = 'l10n_br_account_product.l10n_br_account_product_nfe_form'
        nfe_tree = 'l10n_br_account_product.l10n_br_account_product_nfe_tree'
        nfe_views = {'form': nfe_form, 'tree': nfe_tree}

        if active_id and not fiscal_document_code:
            invoice = self.browse(active_id)
            fiscal_document_code = invoice.fiscal_document_id.code

        if nfe_views.get(view_type) and fiscal_document_code == u'55':
            view_id = self.env.ref(nfe_views.get(view_type)).id

        return super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)

    # TODO Imaginar em não apagar o internal number para nao ter a necessidade
    # de voltar a numeracão
    @api.multi
    def action_cancel_draft(self):
        result = super(AccountInvoice, self).action_cancel_draft()
        self.write({
            'internal_number': False,
            'nfe_access_key': False,
            'nfe_status': False,
            'nfe_date': False,
            'nfe_export_date': False})
        return result

    @api.multi
    def nfe_check(self):
        if self.env.context.get('fiscal_document_code', '') == '55':
            result = txt.validate(self)
            return result

    @api.multi
    def action_number(self):
        # TODO: not correct fix but required a fresh values before reading it.
        self.write({})

        for invoice in self:
            if invoice.issuer == '0':
                sequence_obj = self.env['ir.sequence']
                sequence = sequence_obj.browse(
                    invoice.document_serie_id.internal_sequence_id.id)
                invalid_number = self.env[
                    'l10n_br_account.invoice.invalid.number'].search(
                    [('number_start', '<=', sequence.number_next),
                     ('number_end', '>=', sequence.number_next),
                     ('document_serie_id', '=', invoice.document_serie_id.id),
                     ('state', '=', 'done')])

                if invalid_number:
                    raise UserError(
                        _(u'Número Inválido !'),
                        _("O número: %s da série: %s, esta inutilizado") % (
                            sequence.number_next,
                            invoice.document_serie_id.name))

                seq_number = sequence_obj.get_id(
                    invoice.document_serie_id.internal_sequence_id.id)
                date_time_invoice = (invoice.date_hour_invoice or
                                     fields.datetime.now())
                date_in_out = invoice.date_in_out or fields.datetime.now()
                self.write(
                    {'internal_number': seq_number,
                     'number': seq_number,
                     'date_hour_invoice': date_time_invoice,
                     'date_in_out': date_in_out}
                )

                if not invoice.account_payment_ids and \
                        invoice.nfe_version == '4.00':
                    raise UserError(
                        _(u'A nota fiscal deve conter dados de pagamento')
                    )
                elif invoice.amount_change < 0:
                    raise UserError(
                        _(u'O total de pagamentos deve ser maior ou igual ao '
                          u'total da nota.\nResta realizar o pagamento de '
                          u'%0.2f' % invoice.amount_change)
                    )
                for item, payment in enumerate(
                        invoice.account_payment_line_ids):
                    payment.number = str(item + 1).zfill(3)

        return True

    @api.onchange('type')
    def onchange_type(self):
        ctx = dict(self.env.context)
        ctx.update({'type': self.type})
        self.fiscal_category_id = (self.with_context(ctx).
                                   _default_fiscal_category())

    @api.onchange('fiscal_document_id')
    def onchange_fiscal_document_id(self):
        if self.fiscal_type == 'product':
            if self.issuer == '0':
                series = [doc_serie for doc_serie in
                          self.company_id.document_serie_product_ids if
                          doc_serie.fiscal_document_id.id ==
                          self.fiscal_document_id.id and doc_serie.active]

                if not series:
                    action = self.env.ref(
                        'l10n_br_account.'
                        'action_l10n_br_account_document_serie_form')
                    msg = _(u'Você deve ser uma série de documento fiscal'
                            u'para este documento fiscal.')
                    raise RedirectWarning(
                        msg, action.id, _(u'Criar uma nova série'))
                self.document_serie_id = series[0]

    @api.onchange('fiscal_category_id', 'fiscal_position_id')
    def onchange_fiscal(self):
        if self.company_id and self.partner_id and self.fiscal_category_id:
            if self.fiscal_category_id.property_journal:
                self.journal_id = self.fiscal_category_id.property_journal
            else:
                raise UserError(
                    _("Nenhum Diário !\n"
                      "Categoria fiscal: '%s', não tem um diário contábil "
                      "para a empresa %s") % (self.fiscal_category_id.name,
                                              self.company_id.name))
            kwargs = {
                'company_id': self.company_id,
                'partner_id': self.partner_id,
                'partner_invoice_id': self.partner_id,
                'partner_shipping_id': self.partner_id,
            }
            self.fiscal_position_id = \
                self._fiscal_position_map(**kwargs) or self.fiscal_position_id

    @api.multi
    def action_date_assign(self):
        for inv in self:
            if not inv.date_hour_invoice:
                date_hour_invoice = fields.Datetime.context_timestamp(
                    self, datetime.datetime.now())
            else:
                if inv.issuer == '1':
                    date_move = inv.date_in_out
                else:
                    date_move = inv.date_hour_invoice
                date_hour_invoice = fields.Datetime.context_timestamp(
                    self, datetime.datetime.strptime(
                        date_move, tools.DEFAULT_SERVER_DATETIME_FORMAT
                    )
                )
            date_invoice = date_hour_invoice.strftime(
                tools.DEFAULT_SERVER_DATE_FORMAT)
            res = self.onchange_payment_term_date_invoice(
                inv.payment_term.id, date_invoice)
            if res and res['value']:
                res['value'].update({
                    'date_invoice': date_invoice
                })
                date_time_now = fields.datetime.now()
                if not inv.date_hour_invoice:
                    res['value'].update({'date_hour_invoice': date_time_now})
                if not inv.date_in_out:
                    res['value'].update({'date_in_out': date_time_now})
                inv.write(res['value'])
        return True

    # TODO: Reavaliar a necessidade do método
    # @api.multi
    # def button_reset_taxes(self):
    #     ait = self.env['account.invoice.tax']
    #     for invoice in self:
    #         invoice.read()
    #         costs = []
    #         company = invoice.company_id
    #         if invoice.amount_insurance:
    #             costs.append((company.insurance_tax_id,
    #                           invoice.amount_insurance))
    #         if invoice.amount_freight:
    #             costs.append((company.freight_tax_id,
    #                           invoice.amount_freight))
    #         if invoice.amount_costs:
    #             costs.append((company.other_costs_tax_id,
    #                           invoice.amount_costs))
    #         for tax, cost in costs:
    #             ait_id = ait.search([
    #                 ('invoice_id', '=', invoice.id),
    #                 ('tax_group_id', '=', tax.tax_group_id.id),
    #             ])
    #             vals = {
    #                 'tax_amount': cost,
    #                 'name': tax.name,
    #                 'sequence': 1,
    #                 'invoice_id': invoice.id,
    #                 'manual': True,
    #                 'base_amount': cost,
    #                 'base_code_id': tax.base_code_id.id,
    #                 'amount': cost,
    #                 'base': cost,
    #                 'account_analytic_id':
    #                     tax.account_analytic_collected_id.id or False,
    #                 'account_id': tax.account_paid_id.id,
    #             }
    #             if ait_id:
    #                 ait_id.write(vals)
    #             else:
    #                 ait.create(vals)
    #     return {}

    @api.multi
    def open_fiscal_document(self):
        """return action to open NFe form"""
        result = super(AccountInvoice, self).open_fiscal_document()
        result['name'] = _('NF-e')
        return result

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise UserError(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)
             # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise UserError(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))
             # if inv.payment_term:
            #     total_fixed = total_percent = 0
            #     for line in inv.payment_term.line_ids:
            #         if line.value == 'fixed':
            #             total_fixed += line.value_amount
            #         if line.value == 'procent':
            #             total_percent += line.value_amount
            #     total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
            #     if (total_fixed + total_percent) > 100:
            #         raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))
             # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []

            res_amount_currency = total_currency
            ctx['date'] = date_invoice

            for i, t in enumerate(inv.account_payment_line_ids):

                if inv.currency_id != company_currency:
                    amount_currency = company_currency.with_context(ctx).compute(t.amount_net, inv.currency_id)
                else:
                    amount_currency = False
                 # last line: add the diff
                res_amount_currency -= amount_currency or 0
                if i + 1 == len(totlines):
                    amount_currency += res_amount_currency

                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': t.amount_net,
                    'account_id': inv.account_id.id,
                    'date_maturity': t.date_due,
                    'amount_currency': diff_currency and amount_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref + '/' + t.number,
                })

            if not inv.account_payment_line_ids:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })

            # if inv.payment_term:
            #     totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            # if totlines:
            #     res_amount_currency = total_currency
            #     ctx['date'] = date_invoice
            #     for i, t in enumerate(totlines):
            #         if inv.currency_id != company_currency:
            #             amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
            #         else:
            #             amount_currency = False
            #
            #         # last line: add the diff
            #         res_amount_currency -= amount_currency or 0
            #         if i + 1 == len(totlines):
            #             amount_currency += res_amount_currency
            #
            #         iml.append({
            #             'type': 'dest',
            #             'name': name,
            #             'price': t[1],
            #             'account_id': inv.account_id.id,
            #             'date_maturity': t[0],
            #             'amount_currency': diff_currency and amount_currency,
            #             'currency_id': diff_currency and inv.currency_id.id,
            #             'ref': ref,
            #         })

            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise UserError(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.supplier_invoice_number or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
             # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
        self._log_event()
        return True
