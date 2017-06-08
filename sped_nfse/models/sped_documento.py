# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import re
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
            'tipo_cpfcnpj': 2 if participante.is_company else 1,,
            'cpf_cnpj': re.sub('[^0-9]', '', participante.cnpj_cpf or ''),
            'razao_social': participante.razao_social or '',
            'logradouro': participante.endereco or '',
            'numero': participante.numero or '',
            'complemento': participante.complemento or '',
            'bairro': participante.bairro or 'Sem Bairro',
            'cidade': '%s%s' % (participante.municipio_id.estado_id.codigo_ibge,
                                participante.municipio_id.codigo_ibge),
            'cidade_descricao': participante.cidade or '',
            'uf': participante.estado or '',
            'cep': re.sub('[^0-9]', '', participante.cep),
            'inscricao_municipal': re.sub('[^0-9]', '', participante.im),
            'email': participante.email or '',
        }

    def monta_nfse(self):
        empresa = self.empresa_id
        itens = self.item_ids
        rps = [
            {
                'assinatura': '123-faltando',
                'serie': self.serie,
                'numero': self.numero,
                'data_emissao': self.data_emissao,
                'codigo_atividade': item.produto_id.servico_id.codigo,
                'total_servicos': item.valor_produtos,
                'total_deducoes': '3.00-faltando',
                'prestador': {
                    'inscricao_municipal': self.empresa_id.im
                },
                'tomador': self._monta_nfse_tomador(self),
                'codigo_atividade': '07498-faltando',
                'aliquota_atividade': '5.00-faltando',
                'descricao': 'Venda de servico-faltando'
            }
        ]

        nfse = {
            'cpf_cnpj': empresa.cnpj_cpf,
            'data_inicio': self.data_entrada_saida,
            'data_fim': self.data_entrada_saida,
            'lista_rps': rps
        }
        return nfse
