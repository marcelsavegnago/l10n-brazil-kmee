# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from openerp.addons.sped_fiscal.efd import icms_ipi as gerador


class SpedFiscal(models.Model):

    _name = 'sped.fiscal'
    _description = 'Emissor do Sped Fiscal: ICMS/IPI'

    name = fields.Char()

    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        select=True,
        required=True,
        default=lambda self: self.env.user.company_id.id or '',
    )
    arquivo_remessa = fields.Binary(
        string='Arquivo de remessa',
        readonly=True
    )
    arquivo_remessa_nome = fields.Char(
        name='Nome arquivo',
    )

    @api.multi
    def action_create_file(self):
        self.ensure_one()
        arquivo_remessa = gerador.gera_arquivo(self)
        self.write({
            'arquivo_remessa': arquivo_remessa,
        })
