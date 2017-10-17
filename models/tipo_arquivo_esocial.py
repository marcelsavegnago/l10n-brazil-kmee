# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

<<<<<<< HEAD
<<<<<<< HEAD
from odoo import api, fields, models


class TipoArquivoEsocial(models.Model):
    _name = 'esocial.tipo_arquivo_esocial'
    _description = 'Tipos de Arquivo do eSocial'
=======
from odoo import api, fields, models, _


class AgenteCausador(models.Model):
    _name = 'esocial.tipo_dependente'
    _description = 'Tipos de Dependente'
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
from odoo import api, fields, models


class TipoArquivoEsocial(models.Model):
    _name = 'esocial.tipo_arquivo_esocial'
    _description = 'Tipos de Arquivo do eSocial'
>>>>>>> 84247a3... [ADD] tabelas 9 e 10 feitas
    _order = 'codigo'
    _sql_constraints = [
        ('codigo',
         'unique(codigo)',
         'Este código já existe !'
         )
    ]

    codigo = fields.Char(
<<<<<<< HEAD
<<<<<<< HEAD
        size=6,
=======
        size=2,
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
        size=6,
>>>>>>> 84247a3... [ADD] tabelas 9 e 10 feitas
        string='Codigo',
        required=True,
    )
    descricao = fields.Char(
        string='Descrição',
        required=True,
    )
    name = fields.Char(
        compute='_compute_name',
        store=True,
    )

    @api.onchange('codigo')
    def _valida_codigo(self):
        for tipo in self:
            if tipo.codigo:
<<<<<<< HEAD
<<<<<<< HEAD
                if tipo.codigo[0] == 'S' and tipo.codigo[2:].isdigit():
                    tipo.codigo = tipo.codigo.zfill(6)
=======
                if tipo.codigo.isdigit():
                    tipo.codigo = tipo.codigo.zfill(2)
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
=======
                if tipo.codigo[0] == 'S' and tipo.codigo[2:].isdigit():
                    tipo.codigo = tipo.codigo.zfill(6)
>>>>>>> 84247a3... [ADD] tabelas 9 e 10 feitas
                else:
                    res = {'warning': {
                        'title': _('Código Incorreto!'),
                        'message': _('Campo Código somente aceita números! - Corrija antes de salvar')
                    }}
                    tipo.codigo = False
                    return res

    @api.depends('codigo', 'descricao')
    def _compute_name(self):
        for tipo in self:
            tipo.name = tipo.codigo + '-' + tipo.descricao
