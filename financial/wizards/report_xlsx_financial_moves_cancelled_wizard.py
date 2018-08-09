# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE INFORMATICA LTDA
#    Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

from datetime import datetime
from openerp import fields, models, api, _


class ReportXlsxFinancialFinancialMovesCancelledWizard(models.TransientModel):
    _name = b'report.xlsx.financial.moves.cancelled.wizard'
    _description = 'Report Xlsx Financial Moves Cancelled Wizard'

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company'
    )
    type = fields.Selection(
        string=_('Type'),
        required=True,
        selection=[
            ('2receive', _('To Receive')),
            ('2pay', _('To Pay'))
        ],
        default='2receive',
    )
    date_from = fields.Date(
        string=_("Date From"),
        required=True,
        default=datetime.now().strftime('%Y-%m-01'),
    )
    date_to = fields.Date(
        string=_("Date To"),
        required=True,
        default=datetime.now().strftime('%Y-12-31'),
    )

    @api.multi
    def generate_report(self):
        self.ensure_one()

        return self.env['report'].get_action(
            self,
            report_name='report_xlsx_financial_moves_cancelled'
        )
