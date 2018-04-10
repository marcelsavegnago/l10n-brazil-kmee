# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals
from odoo import fields, models


class SpedAliquotaISS(models.Model):
    _name = b'sped.aliquota.iss'
    _description = 'Alíquotas do ISS'
    _rec_name = 'al_iss'
    _order = 'servico_id, municipio_id, al_iss'

    servico_id = fields.Many2one(
        'sped.servico',
        string='Serviço',
        ondelete='cascade',
        required=True,
    )
    municipio_id = fields.Many2one(
        comodel_name='l10n_br_base.city',
        string='Município',
        ondelete='restrict',
        required=True,
    )
    al_iss = fields.Float(
        string='Alíquota',
        required=True,
        digits=(5, 2),
    )
    codigo = fields.Char(
        string='Código específico',
        size=10,
    )
