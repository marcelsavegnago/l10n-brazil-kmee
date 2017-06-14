# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

from odoo import fields, models


class SpedEmpresa(models.Model):
    _inherit = 'sped.empresa'

    certificado_id = fields.Many2one(
        comodel_name='sped.certificado',
        string='Certificado digital',
    )
    logo_danfse = fields.Binary(
        string='Logo no DANFSE',
        attachment=True,
    )
    mail_template_nfse_autorizada_id = fields.Many2one(
        comodel_name='mail.template',
        string='Modelo de email para NFS-e autorizada',
        #domain=[('model_id', '=', ref('sped.model_sped_documento'))],
    )
    mail_template_nfse_cancelada_id = fields.Many2one(
        comodel_name='mail.template',
        string='Modelo de email para NFS-e cancelada',
        #domain=[('model_id', '=', ref('sped.model_sped_documento'))],
    )
    mail_template_nfse_denegada_id = fields.Many2one(
        comodel_name='mail.template',
        string='Modelo de email para NFS-e denegada',
        #domain=[('model_id', '=', ref('sped.model_sped_documento'))],
    )
    mail_template_nfse_cce_id = fields.Many2one(
        comodel_name='mail.template',
        string='Modelo de email para CC-e de NFS-E',
        #domain=[('model_id', '=', ref('sped.model_sped_documento'))],
    )

    def processador_nfse(self):
        self.ensure_one()

        from pytrustnfe.nfs import paulistana as processador

        # TODO: Chavear entre as cidades
        # from pytrustnfe.nfse.betha as processador
        # from pytrustnfe.nfse.ginfes as processador
        # from pytrustnfe.nfse.issintel as processador
        # from pytrustnfe.nfse.saatri as processador
        # from pytrustnfe.nfse.webiss as processador

        return processador
