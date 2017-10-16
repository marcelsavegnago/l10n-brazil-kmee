# -*- coding: utf-8 -*-

from odoo import fields, models, api

<<<<<<< HEAD
class TipoInscricao(models.Model):
=======
class TiposInscricao(models.Model):
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
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
        string='Nome',
=======
        string='Descrição',
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
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