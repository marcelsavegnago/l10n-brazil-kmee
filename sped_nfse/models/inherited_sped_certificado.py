# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals
import logging
import base64


from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.certificado import Certificado
except ImportError:
    _logger.debug('Cannot import pytrustnfe')

CERTIFICADOS = {}


class SpedCertificado(models.Model):
    _inherit = 'sped.certificado'

    def certificado_nfse(self):

        if self.id in CERTIFICADOS:
            return CERTIFICADOS[self.id]

        self.ensure_one()
        cert_pfx = self.arquivo.decode('base64')

        cert = Certificado(
            cert_pfx, self.senha)

        CERTIFICADOS[self.id] = cert

        return cert
