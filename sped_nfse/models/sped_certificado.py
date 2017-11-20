# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE INFORMATICA
#   Daniel Sadamo <daniel.sadamo@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

import base64
import logging
import tempfile

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import pybrasil.certificado as Cert
except (ImportError, IOError) as err:
    _logger.debug(err)


CERTIFICADOS = {}


class SpedCertificado(models.Model):
    _inherit = 'sped.certificado'

    def certificado_nfse(self):
        self.ensure_one()

        if self.id in CERTIFICADOS:
            return CERTIFICADOS[self.id]

        cert = self.with_context({'bin_size': False}).arquivo
        arq = tempfile.NamedTemporaryFile(delete=False)
        arq.seek(0)
        arq.write(base64.decodebytes(cert))
        arq.flush()

        cert = Cert.Certificado()
        cert.arquivo = arq.name
        cert.senha = self.senha

        cert.prepara_certificado_arquivo_pfx()

        CERTIFICADOS[self.id] = cert

        return cert
