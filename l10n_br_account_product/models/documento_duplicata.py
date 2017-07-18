# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from openerp import api, fields, models
from odoo.addons.financial.constants import FINANCIAL_DEBT_2RECEIVE, \
    FINANCIAL_DEBT_2PAY


class SpedDocumentoDuplicata(models.Model):
    _name = 'sped.documento.duplicata'
    _description = 'Duplicatas do Documento Fiscal'
    _order = 'documento_id, data_vencimento'
    # _rec_name = 'numero'

    documento_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Documento',
        ondelete='cascade',
    )
    pagamento_id = fields.Many2one(
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
    valor = fields.Monetary(
        string='Valor',
        digits=(18, 2),
        required=True,
    )

    @api.depends('pagamento_id', 'documento_id')
    def _check_pagamento_id_documento_id(self):
        for duplicata in self:
            if duplicata.pagamento_id:
                if not duplicata.documento_id:
                    duplicata.documento_id = \
                        duplicata.pagamento_id.documento_id.id
                elif duplicata.documento_id.id != \
                        duplicata.pagamento_id.documento_id.id:
                    duplicata.documento_id = \
                        duplicata.pagamento_id.documento_id.id

    financial_move_ids = fields.One2many(
        comodel_name='financial.move',
        inverse_name='sped_documento_duplicata_id',
        string='Lançamentos Financeiros',
        copy=False
    )

    def prepara_financial_move(self):
        dados = {
            'date_document': self.documento_id.data_emissao,
            'participante_id': self.documento_id.participante_id,
            'partner_id': self.documento_id.participante_id.partner_id.id,
            'empresa_id': self.documento_id.empresa_id.id,
            'company_id': self.documento_id.empresa_id.company_id.id,
            'doc_source_id': 'sped.documento,' + str(self.documento_id.id),
            'currency_id': self.documento_id.currency_id.id,
            'sped_documento_id': self.documento_id.id,
            'sped_documento_duplicata_id': self.id,
            'document_type_id':
                self.documento_id.financial_document_type_id.id,
            'account_id': self.documento_id.financial_account_id.id,
            'date_maturity': self.data_vencimento,
            'amount_document': self.valor,
            'document_number':
                '{0.serie}-{0.numero:0.0f}-{1.numero}/{2}'.format(
                    self.documento_id, self,
                    len(self.documento_id.duplicata_ids)),
        }

        dados['type'] = FINANCIAL_DEBT_2PAY

        return dados
