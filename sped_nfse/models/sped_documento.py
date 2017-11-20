# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import re
import datetime
import mock
import os.path
import unittest
from pytrustnfe.certificado import Certificado
from pytrustnfe.nfse.ginfes import xml_recepcionar_lote_rps
from pytrustnfe.nfse.ginfes import recepcionar_lote_rps
from pytrustnfe.nfse.ginfes import xml_cancelar_nfse
from pytrustnfe.nfse.ginfes import cancelar_nfse
from collections import Counter
from lxml import etree


class SpedDocumento(models.Model):

    _inherit = 'sped.documento'

    def envia_nfse(self):
        cert = self.empresa_id.certificado_id.certificado_nfse()
        senha = bytes(cert.senha.encode())
        arquivo = cert.stream_certificado
        # pfx_source = open(os.path.join(self.empresa_id.certificado_id.arquivo, 'teste.pfx'), 'r').read()
        pfx = Certificado(arquivo, senha)

        dados_nfse = self.monta_nfse()

        lote_rps = xml_recepcionar_lote_rps(
            certificado=pfx, nfse=dados_nfse,
            ambiente=self.empresa_id.ambiente_nfse)

        self.validar_schema(lote_rps)
        retorno = recepcionar_lote_rps(certificado=pfx, xml=lote_rps,
                                       ambiente=self.empresa_id.ambiente_nfse)
        print (retorno)


    def _monta_nfse_tomador(self, dest):
        participante = self.participante_id

        return {
            'tipo_cpfcnpj': 1 if participante.tipo_pessoa == 'F' else 2,
            'cnpj_cpf': re.sub('[^0-9]', '', participante.cnpj_cpf or ''),
            'razao_social': participante.razao_social or '',
            'logradouro': participante.endereco or '',
            'numero': participante.numero or '',
            'complemento': participante.complemento or '',
            'bairro': participante.bairro or 'Sem Bairro',
            'cidade': participante.municipio_id.codigo_ibge[:4],
            'cidade_descricao': participante.cidade or '',
            'uf': participante.estado or '',
            'cep': re.sub('[^0-9]', '', participante.cep),
            'inscricao_municipal': re.sub('[^0-9]', '', participante.im or ''),
            'email': participante.email or '',
        }

    def _monta_nfse_prestador(self, dest):
        participante = self.empresa_id

        return {
            'cnpj': re.sub('[^0-9]', '', participante.cnpj_cpf or ''),
            'inscricao_municipal': re.sub('[^0-9]', '', participante.im or ''),
        }

    def monta_nfse(self):
        empresa = self.empresa_id
        itens = self.item_ids
        tomador = self._monta_nfse_tomador(self)
        prestador = self._monta_nfse_prestador(self)
        codigos = Counter(
            item.produto_id.servico_id.codigo for item in itens)
        codigo_servico = codigos.most_common()[0][0]
        data_emissao = fields.Datetime.from_string(self.data_hora_emissao)

        rps = [
            {
                'assinatura': '123-faltando', #TODO
                'natureza_operacao': '2', #TODO lista de 1 a 6
                'optante_simples': '2', #TODO
                'incentivador_cultural': '2', #TODO
                'numero': int(self.numero),
                'serie': self.serie,
                'tipo_rps': '1', # TODO
                'data_emissao': data_emissao.strftime('%Y-%m-%dT%H:%M:%S'),
                'status': '1', # TODO
                'valor_servico': sum(item.vr_operacao_readonly for
                                          item in itens),
                'codigo_servico': codigo_servico,
                'iss_retido': '2', # TODO: Tornar Dinamico
                'descricao': 'Venda de servico-faltando', #TODO
                'codigo_municipio': tomador.get('cidade'),
                'tomador': tomador,
                'prestador': prestador,
                # TODO: Identificação do orgão gerador
            }
        ]

        nfse = {
            'numero_lote': '3', # TODO: Criar numero Lote
            'cnpj_prestador': re.sub('[^0-9]', '', empresa.cnpj_cpf or ''),
            'inscricao_municipal': re.sub('[^0-9]', '', empresa.im or ''),
            'data_inicio': self.create_date,
            'data_fim': self.data_hora_emissao,
            'lista_rps': rps,
        }
        return nfse

    def validar_schema(self, lote_rps):
        # TODO: automatizar path do arquivo de validação
        # Colocar o path do caminho do arquivo
        arquivo_esquema = '/home/sadamo/projetos/kmee/produto11/src/pytrustnfe/pytrustnfe/nfse/ginfes/schemas_v301/servico_enviar_lote_rps_envio_v03.xsd'
        esquema = etree.XMLSchema(etree.parse(arquivo_esquema))
        esquema.validate(etree.fromstring(lote_rps))
        namespace = '{http://www.portalfiscal.inf.br/nfe}'
        retorno = "\n".join(
            [x.message.replace(namespace, '') for x in esquema.error_log])
        return retorno
