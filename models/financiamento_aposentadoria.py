# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models

class FinanciamentoAposentadoria(models.Model):
    _name = 'esocial.financiamento_aposentadoria'
    _description = 'Financiamento da Aposentadoria Especial e Redução' \
                   'do Tempo de Contribuição'
    _order = 'name'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=1,
        string='Codigo',
        required=True,
    )
    nome = fields.Char(
        string='Nome',
        required=True,
    )
    name = fields.Char(
<<<<<<< HEAD
<<<<<<< HEAD
        compute='_compute_name',
=======
        compute='_calcula_name',
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        compute='_compute_name',
>>>>>>> 565ad17... [FIX] PEP8
        store=True,
    )

    @api.onchange('codigo')
    def _valida_codigo(self):
        for financiamento in self:
            if financiamento.codigo:
                if financiamento.codigo.isdigit():
                    financiamento.codigo = financiamento.codigo.zfill(1)
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números!'
                                     ' - Corrija antes de salvar')
                    }}
                    financiamento.codigo = False
                    return res

    @api.depends('codigo', 'nome')
<<<<<<< HEAD
<<<<<<< HEAD
    def _compute_name(self):
=======
    def _calcula_name(self):
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
    def _compute_name(self):
>>>>>>> 565ad17... [FIX] PEP8
        for financiamento in self:
            financiamento.name = financiamento.codigo + '-' + \
                                 financiamento.nome
