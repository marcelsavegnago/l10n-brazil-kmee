# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Daniel Sadamo - KMEE INFORMATICA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models

OPERATION_NATURE = [
    ('venda', u'Venda'),
    ('revenda', u'Revenda'),

]

OPERATION_POSITION = [
    ('interestadual', u'Interestadual'),
    ('dentro_estado', u'Dentro do estado'),
    ('exportacao', u'Exportação'),

]

PRODUCT_ORIGIN = [
    ('0', u'0 - Nacional, exceto as indicadas nos códigos 3 a 5'),
    ('1', u'1 - Estrangeira - Importação direta, exceto a indicada no código'
     ' 6'),
    ('2', u'2 - Estrangeira - Adquirida no mercado interno, exceto a indicada'
     u' no código 7'),
    ('3', u'3 - Nacional, mercadoria ou bem com Conteúdo de Importação'
     ' superior a 40% (quarenta por cento)'),
    ('4', u'4 - Nacional, cuja produção tenha sido feita em conformidade com'
     u' os processos produtivos básicos de que tratam o Decreto-Lei nº 288/67,'
     u' e as Leis nºs 8.248/91, 8.387/91, 10.176/01 e 11.484/07'),
    ('5', u'5 - Nacional, mercadoria ou bem com Conteúdo de Importação'
     u' inferior ou igual a 40% (quarenta por cento)'),
    ('6', u'6 - Estrangeira - Importação direta, sem similar nacional,'
     u' constante em lista de Resolução CAMEX'),
    ('7', u'7 - Estrangeira - Adquirida no mercado interno, sem similar'
     u' nacional, constante em lista de Resolução CAMEX'),
    ('8', u'8 - Nacional, mercadoria ou bem com Conteúdo de Importação'
     u' superior a 70%')
]

TERM = [
    ('curto', 'Curto prazo'),
    ('longo', 'Longo prazo')
]

OPERATION_PURPOSE = [
    ('operacional', u'Operacional'),
    ('financeiro', u'Financeiro'),
]

MOVE_TYPE = [
    ('receita', 'Receita'),
]
class AccountMoveTemplateRule(models.Model):
    _name = 'account.move.template.rule'

    fiscal_document_id = fields.Many2one(
        comodel_name='l10n_br_account.fiscal.document',
        string=u'Tipo do documento'
    )
    # TODO: verificar origem desse campo
    account_move_category_id = fields.Char()
    operation_nature = fields.Selection(selection=OPERATION_NATURE)
    operation_position = fields.Selection(selection=OPERATION_POSITION)
    # TODO: verificar se sera criado modelo para o tipo de produto
    product_type = fields.Char()
    product_origin = fields.Selection(selection=PRODUCT_ORIGIN)
    term = fields.Selection(selection=TERM)
    # TODO: qual a melhor forma de estruturar?
    # operation_purpose = fields.Selection(selection=OPERATION_PURPOSE)
    account_move_type = fields.Selection(selection=MOVE_TYPE)
    credit_account_id = fields.Many2one(
        comodel_name='acccount.account', string=u'Conta de credito'
    )
    debit_account_id = fields.Many2one(
        comodel_name='acccount.account', string=u'Conta de debito'
    )
    debit_compensation_account_id = fields.Many2one(
        comodel_name='acccount.account', string=u'Conta de compensaçao de '
                                                u'debito'
    )

    def _map_domain(self):
        pass

    def map_account(self, **kwargs):
        """ Parametros da tabela de decisão:
         - company_id, document_type_id,
                    account_move_category_id, operation_nature,
                    operation_position, product_type, product_origin, term,
                    operation_purpose, account_move_type
        :return: o objeto account.account
        """
        return True
        # search ?
        #
        # ret