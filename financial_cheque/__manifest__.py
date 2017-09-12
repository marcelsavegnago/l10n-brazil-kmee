# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Financial Cheque',
    'summary': 'Controle de Cheques no Financeiro',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.odoobrasil.org.br',
    'depends': [
        #'l10n_br_financial',
        'l10n_br_base',
        'financial',
    ],
    'data': [
        'security/financial_cheque_security.xml',
        'views/financial_cheque_view.xml',
        'views/financial_cheque_movimento_base_view.xml',
        'views/financial_cheque_movimento_receber_view.xml',
        'views/financial_cheque_movimento_enviar_view.xml',
        #'views/financeiro_deposito_cheque.xml',
        #'views/financeiro_estorno_cheque.xml',
        #'views/financial_move.xml',
    ],
    #'demo': [
        #'demo/financeiro_tipo_documento.xml',
        #'demo/financeiro_cheque.xml',
        #'demo/account_payment_mode.xml',
        #'demo/account_payment_method.xml',
    #],
    'installable': True,
}
