# -*- coding: utf-8 -*-
#
# Copyright 2016 KMEE - Luis Felipe Miléo <mileo@kmee.com.br>
# Copyright 2016 KMEE - Hendrix Costa <hendrix.costa@kmee.com.br>
# Copyright 2017 KMEE - Aristides Caldeira <aristides.caldeira@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from pybrasil.feriado.constantes import (
        TIPO_FERIADO, ABRANGENCIA_FERIADO,
    )
except ImportError:
    _logger.warning('Cannot import pybrasil')


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    country_id = fields.Many2one(
        'res.country', string='País',
        related='calendar_id.country_id',
    )
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        related='calendar_id.state_id',
        domain="[('country_id','=',country_id)]",
        readonly=True
    )
    municipio_id = fields.Many2one(
        comodel_name='sped.municipio',
        string='Município',
        related='calendar_id.municipio_id',
        domain="[('estado_id.state_id', '=', state_id)]",
        readonly=True
    )
    leave_kind = fields.Selection(
        string='Leave Kind',
        selection=list(TIPO_FERIADO.items()),
    )
    leave_scope = fields.Selection(
        string='Leave Scope',
        selection=list(ABRANGENCIA_FERIADO.items()),
    )
