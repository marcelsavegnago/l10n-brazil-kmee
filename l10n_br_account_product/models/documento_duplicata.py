# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from openerp import api, fields, models
from openerp.addons.financial.constants import FINANCIAL_DEBT_2RECEIVE, \
    FINANCIAL_DEBT_2PAY


class SpedDocumentoDuplicata(models.Model):
    _name = 'sped.documento.duplicata'
    _description = 'Duplicatas do Documento Fiscal'
    _order = 'invoice_id, data_vencimento'
    # _rec_name = 'numero'

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Documento',
        ondelete='cascade',
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Pagamento',
        ondelete='cascade',
    )
    numero = fields.Char(
        string='Número',
        size=60,
        required=True,
    )
    data_vencimento = fields.Date(
        string='Data de vencimento',
        required=True,
    )
    valor = fields.Float(
        string='Valor',
        digits=(18, 2),
        required=True,
    )

    @api.depends('payment_term_id', 'invoice_id')
    def _check_payment_term_id_invoice_id(self):
        for duplicata in self:
            if duplicata.payment_term_id:
                if not duplicata.invoice_id:
                    duplicata.invoice_id = \
                        duplicata.payment_term_id.invoice_id.id
                elif duplicata.invoice_id.id != \
                        duplicata.payment_term_id.invoice_id.id:
                    duplicata.invoice_id = \
                        duplicata.payment_term_id.invoice_id.id

    financial_move_ids = fields.One2many(
        comodel_name='financial.move',
        inverse_name='sped_documento_duplicata_id',
        string='Lançamentos Financeiros',
        copy=False
    )

    def prepara_financial_move(self):
        dados = {
            'date_document': self.invoice_id.data_emissao,
            # 'participante_id': self.invoice_id.participante_id,
            'partner_id': self.invoice_id.partner_id.id,
            # 'empresa_id': self.invoice_id.empresa_id.id,
            'company_id': self.invoice_id.company_id.id,
            'doc_source_id': 'account.invoice,' + str(self.invoice_id.id),
            'currency_id': self.invoice_id.currency_id.id,
            'sped_invoice_id': self.invoice_id.id,
            'sped_documento_duplicata_id': self.id,
            'document_type_id':
                self.invoice_id.financial_document_type_id.id,
            'account_id': self.invoice_id.financial_account_id.id,
            'date_maturity': self.data_vencimento,
            'amount_document': self.valor,
            'document_number':
                '{0.serie}-{0.numero:0.0f}-{1.numero}/{2}'.format(
                    self.invoice_id, self,
                    len(self.invoice_id.duplicata_ids)),
        }

        dados['type'] = FINANCIAL_DEBT_2PAY

        return dados
