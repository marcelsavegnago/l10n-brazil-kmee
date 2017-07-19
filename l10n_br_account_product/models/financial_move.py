# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from openerp import api, fields, models


class FinancialMove(models.Model):
    _inherit = 'financial.move'

    sped_documento_duplicata_id = fields.Many2one(
        comodel_name="sped.documento.duplicata",
        string="Financial move"
    )
