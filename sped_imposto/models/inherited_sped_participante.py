# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

from odoo import fields, models


class SpedParticipante(models.Model):
    _inherit = 'sped.participante'

    cnae_id = fields.Many2one(
        comodel_name='sped.cnae',
        string='CNAE principal'
    )
