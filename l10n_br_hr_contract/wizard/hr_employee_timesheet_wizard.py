# -*- coding: utf-8 -*-
# (c) 2019 Kmee - Diego Paradeda <diego.paradeda@kmee.com.br>
# (c) 2019 Kmee - Hugo Borges <hugo.borges@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class HrEmployeeTimeSheetWizard(models.TransientModel):
    _inherit = 'hr.employee.timesheet.wizard'

    @api.multi
    def action_print_hr_contracts_py3o(self):
        return self.env['report'].get_action(
            self,
            "l10n_br_hr_contract.report_employees_timesheet"
        )
