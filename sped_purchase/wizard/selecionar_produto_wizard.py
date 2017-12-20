# -*- coding: utf-8 -*-
# Copyright (C) 2017 Gabriel Cardoso de Faria - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api, _


class SelecionarProduto(models.TransientModel):
    _name = b'sped.documento.item.selecionar.produto'

    documento_item_id = fields.Many2one(
        comodel_name='sped.documento.item',
        string='Item',
    )

    produto_id = fields.Many2one(
        comodel_name='sped.produto',
        related='documento_item_id.produto_id'
    )
