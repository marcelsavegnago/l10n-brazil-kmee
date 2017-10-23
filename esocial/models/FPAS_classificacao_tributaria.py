# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
#   Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from odoo import api, fields, models

class FPASClassificacaoTributaria(models.Model):
    _name = 'esocial.tributaria_fpas'
    _description = 'Compatibilidade entre FPAS e Classificação Tributária'

    name = fields.Char(
        string ='Classificação Tributária',
    )
