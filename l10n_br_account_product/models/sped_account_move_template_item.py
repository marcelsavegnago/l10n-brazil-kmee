# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATIDA LTDA
#   Aristides Caldeira <aristides.caldeira@kmee.com.br>
#   Daniel Sadamo <daniel.sadamo@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import division, print_function, unicode_literals

from openerp import api, fields, models
from ..constantes import (
    CAMPO_DOCUMENTO_FISCAL,
    CAMPO_DOCUMENTO_FISCAL_ITEM,
    ACCOUNT_AUTOMATICO,
)


class SpedAccountMoveTemplateItem(models.Model):
    _name = b'sped.account.move.template.item'
    _description = 'Item do modelo de partidas dobradas'

    template_id = fields.Many2one(
        comodel_name='sped.account.move.template',
        string='Modelo',
        required=True,
        ondelete='cascade',
    )
    campo = fields.Selection(
        selection=CAMPO_DOCUMENTO_FISCAL,
        string='Campo',
        required=True,
    )
    account_debito_id = fields.Many2one(
        comodel_name='account.account',
        string='Débito',
        domain=[('type', '!=', 'view')],
    )
    account_credito_id = fields.Many2one(
        comodel_name='account.account',
        string='Crédito',
        domain=[('type', '!=', 'view')],
    )
    account_automatico_debito = fields.Selection(
        selection=ACCOUNT_AUTOMATICO,
        string='Trazer débito do',
    )
    account_automatico_credito = fields.Selection(
        selection=ACCOUNT_AUTOMATICO,
        string='Trazer crédito do',
    )
