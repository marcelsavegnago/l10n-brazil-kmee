# -*- coding: utf-8 -*-
# Copyright (C) 2016-TODAY Akretion <http://www.akretion.com>
#   @author Magno Costa <magno.costa@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _order = 'date_maturity, date desc, id desc'

    _sql_constraints = [
        (
            'credit_debit1', 'Check(1=1)',
            'Wrong credit or debit value in accounting entry !'
        ),
        (
            'credit_debit2', 'Check(1=1)',
            'Wrong credit or debit value in accounting entry !'
        ),
    ]


AccountMoveLine()
