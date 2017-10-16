# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models, _

CATEGORIA_GRUPO = (
    ('1', 'Empregado e Trabalhador Temporário'),
    ('2', 'Avulso'),
    ('3', 'Agente Público'),
    ('4', 'Cessão'),
    ('7', 'Contribuinte Individual'),
    ('9', 'Bolsista'),
)


class CategoriaTrabalhador(models.Model):
    _name = 'esocial.categoria_trabalhador'
    _description = 'Categorias de Trabalhadores'
    _order = 'name'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
        size=3,
        string='Codigo',
        required=True,
    )
    nome = fields.Char(
        string='Nome',
        required=True,
    )
    descricao = fields.Text(
        string='Descrição',
    )
    grupo = fields.Selection(
        string='Grupo',
        selection=CATEGORIA_GRUPO,
        default='1',
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
        for categoria in self:
            if categoria.codigo:
                if categoria.codigo.isdigit():
                    categoria.codigo = categoria.codigo.zfill(3)
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números! - Corrija antes de salvar')
                    }}
                    categoria.codigo = False
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
        for categoria in self:
            categoria.name = categoria.codigo + '-' + categoria.nome

