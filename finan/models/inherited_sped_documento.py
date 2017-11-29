# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from pybrasil.data import hoje

except (ImportError, IOError) as err:
    _logger.debug(err)


class SpedDocumento(models.Model):
    _inherit = 'sped.documento'

    carteira_id = fields.Many2one(
        string='Carteira Padrão',
        comodel_name='finan.carteira',
    )
