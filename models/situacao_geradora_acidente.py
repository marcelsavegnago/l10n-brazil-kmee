# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _


class SituacaoGeradora(models.Model):
    _name = 'esocial.situacao_geradora_acidente'
    _description = 'Situação Geradora do Acidente de Trabalho'
    _order = 'name'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=9,
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
        for situacao in self:
            if situacao.codigo:
                if situacao.codigo.isdigit():
                    situacao.codigo = situacao.codigo.zfill(9)
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números!'
                                     ' - Corrija antes de salvar')
                    }}
                    situacao.codigo = False
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
        for situacao in self:
            situacao.name = situacao.codigo + '-' + situacao.nome
