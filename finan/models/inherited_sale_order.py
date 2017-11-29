# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def default_domain(self):
        ids = []
        for carteira in self.participante_id.sped_empresa_id.carteira_ids:
            ids.append(carteira.id)
        ids.append(self.participante_id.sped_empresa_id.carteira_id)
        return [('id', 'in', ids)]

    carteira_id = fields.Many2one(
        string='Carteira',
        comodel_name='finan.carteira',
        domain=default_domain,
    )
    permissao = fields.Boolean(
        compute="compute_permissao",
        default=True,
    )

    @api.multi
    @api.depends('user_id')
    def compute_permissao(self):
        if self.user_id.has_group('finan.GRUPO_CADASTRO_GERENTE'):
            self.permissao = True
        else:
            self.permissao = False
    @api.multi
    @api.onchange('participante_id')
    def compute_carteira(self):
            if self.permissao == False:
                self.carteira_id = self.participante_id.sped_empresa_id.carteira_id
