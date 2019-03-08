# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserWarning

MIS_REPORT_MODE = [
    ('contabil', u'Contábil'),
    ('gerencial', 'Gerencial'),
]


class MisReport(models.Model):

    _inherit = 'mis.report'

    report_mode = fields.Selection(
        string=u'Modalidade de relatório',
        selection=MIS_REPORT_MODE,
        default='contabil'
    )
    considerations = fields.Text(
        string=u'Considerações finais'
    )

    incluir_lancamentos_de_fechamento = fields.Boolean(
        string=u'Incluir lançamentos de fechamento?'
    )

    @api.onchange('incluir_lancamentos_de_fechamento')
    def _onchange_incluir_lancamentos_de_fechamento(self):
        self.ensure_one()

        for kpi_id in self.kpi_ids:
            kpi_id.incluir_lancamentos_de_fechamento = \
                self.incluir_lancamentos_de_fechamento
