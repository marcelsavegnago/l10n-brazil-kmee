# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    participante_id = fields.Many2one(
        comodel_name='sped.participante',
        string='Cliente',
    )

    # @api.onchange('participante_id')
    # def _onchange_participante_id(self):
    #     self.ensure_one()
    #     self.partner_id = self.participante_id.partner_id
