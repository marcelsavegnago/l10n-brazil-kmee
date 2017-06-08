# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import mock
import os.path
import unittest
from pytrustnfe.certificado import Certificado
from pytrustnfe.nfse.paulistana import envio_lote_rps
from pytrustnfe.nfse.paulistana import cancelamento_nfe
from pytrustnfe.nfse.assinatura import Assinatura
from pytrustnfe.nfse.paulistana import sign_tag


class SpedDocumento(models.Model):

    _inherit = 'sped.documento'

    def envia_nfse(self):
        # pfx_source = open(os.path.join(self.caminho, 'teste.pfx'), 'r').read()
        # pfx = Certificado(pfx_source, '123456')

        nfse = self.monta_nfse()
        print (nfse)
        # path = os.path.join(os.path.dirname(__file__), 'XMLs')
        # xml_return = open(os.path.join(
        #     path, 'paulistana_resultado.xml'), 'r').read()
        #
        # with mock.patch(
        #         'pytrustnfe.nfse.paulistana.get_authenticated_client') as client:
        #     retorno = mock.MagicMock()
        #     client.return_value = retorno
        #     retorno.service.EnvioLoteRPS.return_value = xml_return
        #
        #     retorno = envio_lote_rps(pfx, nfse=nfse)
        #
        #     self.assertEqual(retorno['received_xml'], xml_return)
        #     self.assertEqual(retorno['object'].Cabecalho.Sucesso, True)
        #     self.assertEqual(
        #         retorno['object'].ChaveNFeRPS.ChaveNFe.NumeroNFe, 446)
        #     self.assertEqual(
        #         retorno['object'].ChaveNFeRPS.ChaveRPS.NumeroRPS, 6)

    def _monta_nfse_tomador(self, dest):
        participante = self.participante_id

        return {
            'tipo_cpfcnpj': '1',
            'cpf_cnpj': participante.cnpj_cpf,
            'inscricao_municipal': participante.im,
            'razao_social': participante.razao_social,
            'tipo_logradouro': '1',
            'logradouro': participante.endereco,
            'numero': participante.numero,
            'bairro': participante.bairro,
            'cidade': participante.cidade,
            'uf': participante.estado,
            'cep': participante.cep,
        }

    def monta_nfse(self):
        rps = [
            {
                'assinatura': '123',
                'serie': '1',
                'numero': '1',
                'data_emissao': '2016-08-29',
                'codigo_atividade': '07498',
                'total_servicos': '2.00',
                'total_deducoes': '3.00',
                'prestador': {
                    'inscricao_municipal': '123456'
                },
                'tomador': self._monta_nfse_tomador(),
                'codigo_atividade': '07498',
                'aliquota_atividade': '5.00',
                'descricao': 'Venda de servico'
            }
        ]
        nfse = {
            'cpf_cnpj': '12345678901234',
            'data_inicio': '2016-08-29',
            'data_fim': '2016-08-29',
            'lista_rps': rps
        }
        return nfse
