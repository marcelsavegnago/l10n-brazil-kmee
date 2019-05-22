# -*- coding: utf-8 -*-

from openerp import api, fields, models

PAYMENT_MODES_TEF = [
    '03', '04', '10', '11', '13',
]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    pagamento_tef = fields.Boolean(
        string=u"Pagamento TEF",
        help=u"Adiciona o leitor de cartões TEF como forma de Pagamento",
        default=False,
    )

    @api.onchange('sat_payment_mode')
    @api.multi
    def _onchange_sat_payment_mode(self):
        for record in self:
            if record.sat_payment_mode not in PAYMENT_MODES_TEF:
                record.pagamento_tef = False