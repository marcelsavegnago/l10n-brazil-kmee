# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from odoo import api, fields, models, _

from .base_participante import BaseParticipante

class SpedParticipante(BaseParticipante, models.Model):
    _name = b'sped.participante'
    _description = 'Participantes'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner original',
        ondelete='restrict',
        required=True,
    )