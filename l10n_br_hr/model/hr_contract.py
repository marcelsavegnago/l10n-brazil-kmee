# -*- coding: utf-8 -*-
# (c) 2019 Kmee - Diego Paradeda <diego.paradeda@kmee.com.br>
# (c) 2019 Kmee - Hugo Borges <hugo.borges@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    compose_lot = fields.Boolean(
        string='Compose Lot?',
        default=True,
    )
