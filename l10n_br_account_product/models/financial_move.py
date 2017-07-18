# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from openerp import api, fields, models


class FinancialMove(models.Model):
    _name = 'financial.move'

    sped_documento_duplicata_id = fields.Many2one(
        comodel_name="financial.move",
        string="Financial move"
    )
