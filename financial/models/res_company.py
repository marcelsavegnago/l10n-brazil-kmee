# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    adiantar_dia_pagamento_util = fields.Boolean(
        string=u'Adiantar dia de pagamento útil?',
        default=False
    )
