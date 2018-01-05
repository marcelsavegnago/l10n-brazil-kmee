# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import fields, models, api

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======

>>>>>>> 251061b... [FIX] Correções pep8 esocial
class TipoInscricao(models.Model):
=======
class TiposInscricao(models.Model):
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
class TipoInscricao(models.Model):
>>>>>>> 84247a3... [ADD] tabelas 9 e 10 feitas
    _name = "esocial.tipos_inscricao"
    _description = "Tipos de Inscrição"
    _order = 'codigo'

    codigo = fields.Integer(
        string='Codigo',
        required=True,
    )
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    descricao = fields.Text(
<<<<<<< HEAD
<<<<<<< HEAD
        string='Nome',
=======
        string='Descrição',
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
        string='Nome',
>>>>>>> e6f12d3... [ADD] tabelas 5,7 e 8 e algumas correcoes
        required=True,
    )

    name = fields.Char(
        compute='_compute_name',
        store=True,
    )

    @api.depends('codigo', 'descricao')
    def _compute_name(self):
        for tipo in self:
            tipo.name = str(tipo.codigo) + '-' + tipo.descricao
