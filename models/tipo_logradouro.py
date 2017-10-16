# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _


class TipoLogradouro(models.Model):
    _name = 'esocial.tipo_logradouro'
    _description = 'Tipos de Logradouro'
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
        for tipo in self:
            tipo.name = tipo.codigo + '-' + tipo.nome
