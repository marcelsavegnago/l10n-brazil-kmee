# -*- coding: utf-8 -*-
# Copyright (C) 2018  Luiz Felipe do Divino - ABGF - luiz.divino@abgf.gov.br
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    stock_move_journal_id = fields.Many2one(
        string='Diário para Movimentações de Estoque',
        comodel_name='account.journal',
    )
    stock_move_account_income = fields.Many2one(
        string='Conta de Receita',
        comodel_name='account.account',
    )
    stock_move_account_outcome = fields.Many2one(
        string='Conta de Despesa',
        comodel_name='account.account',
    )
