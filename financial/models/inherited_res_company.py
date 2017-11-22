# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    adiantar_dia_pagamento_util = fields.Boolean(
        string=u'Adiantar dia de pagamento útil?',
        default=False
    )

    today_date = fields.Date(
        string='Today Date',
    )

    @api.model
    def cron_update_reference_date_today(self):
        for company in self.env['res.company'].search([]):
            if company.today_date != fields.Date.today():
                company.today_date = fields.Date.today()
