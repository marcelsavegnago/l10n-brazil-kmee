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

    @api.onchange('action')
    def onchange_action(self):
        if self.action == 'exist':
            self.partner_id = self._find_matching_partner()
            self.participante_id = self.partner_id.sped_participante_id
        else:
            self.partner_id = False
            self.participante_id = False

    # @api.onchange('participante_id')
    # def _onchange_participante_id(self):
    #     self.ensure_one()
    #     self.partner_id = self.participante_id.partner_id
