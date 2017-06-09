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
        nfse = self.monta_nfse()

        from pprint import pprint
        pprint (nfse)

    def _monta_nfse_tomador(self, dest):
        participante = self.participante_id

        return {
            'tipo_cpfcnpj': 2 if participante.is_company else 1,
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
            'cep': re.sub('[^0-9]', '', participante.cep or ''),
            'inscricao_municipal': re.sub('[^0-9]', '', participante.im or ''),
            'email': participante.email or '',
        }

    def _monta_nfse_prestador(self, dest):
        prestador = self.empresa_id

        return {
            'cnpj': re.sub(
                '[^0-9]', '', prestador.cnpj_cpf or ''),
            'razao_social': prestador.razao_social or '',
            'inscricao_municipal': re.sub(
                '[^0-9]', '', prestador.im or ''),
            'cidade': '%s%s' % (prestador.municipio_id.estado_id.codigo_ibge,
                                prestador.municipio_id.codigo_ibge),
            'telefone': re.sub('[^0-9]', '', prestador.fone or ''),
            'email': prestador.email or '',
        }


    def monta_nfse(self):
#        res = super(SpedDocumento, self).monta_nfse()

        empresa = self.empresa_id
        descricao = ''
        codigo_servico = ''
        itens = self.item_ids
        for item in itens:
            descricao += item.produto_id.nome + '\n'
            # TODO: Somente o último codigo de servico sera transmitido, isso é correto ?
            codigo_servico = item.produto_id.servico_id.codigo 

        if self.infadfisco:
            descricao += self.infadfisco + '\n'

        if self.infcomplementar:
            descricao += self.infcomplementar + '\n'

        rps = {
                'tomador': self._monta_nfse_tomador(self),
                'prestador': self._monta_nfse_prestador(self),
                'numero': int(self.numero),
                'data_emissao': self.data_emissao,
                'serie': self.serie or '',
                'aliquota_atividade': '0.000',
                'codigo_atividade': re.sub('[^0-9]', '', codigo_servico or ''),
                'municipio_prestacao': self.empresa_id.cidade or '',
                'valor_pis': str("%.2f" % self.vr_pis_proprio),
                'valor_cofins': str("%.2f" % self.vr_cofins_proprio),
                'valor_csll': str("%.2f" % 0.0),
                'valor_inss': str("%.2f" % 0.0),
                'valor_ir': str("%.2f" % 0.0),
                'aliquota_pis': str("%.2f" % 0.0),
                'aliquota_cofins': str("%.2f" % 0.0),
                'aliquota_csll': str("%.2f" % 0.0),
                'aliquota_inss': str("%.2f" % 0.0),
                'aliquota_ir': str("%.2f" % 0.0),
                'valor_servico': str("%.2f" % self.vr_nf),
                'valor_deducao': str("%.2f" % 0.0),
                'descricao': descricao,
                'deducoes': [],
            }

        valor_servico = self.vr_nf
        valor_deducao = 0.0

        cnpj_cpf = self.empresa_id.cnpj_cpf
        data_envio = rps['data_emissao']
        inscr = self.empresa_id.im
        iss_retido = 'N'
        tipo_cpfcnpj = 2 if self.empresa_id.is_company else 1
        codigo_atividade = rps['codigo_atividade']
        # FIXME: Encontrar campo de operação - T - Tributado em São Paulo
        tipo_recolhimento = 'T'

        assinatura = '%s%s%s%s%sN%s%015d%015d%s%s%s' % (
            str(inscr).zfill(8),
            self.serie.ljust(5),
            str(self.numero).zfill(12),
            str(data_envio[0:4] + data_envio[5:7] + data_envio[8:10]),
            str(tipo_recolhimento),
            str(iss_retido),
            round(valor_servico*100),
            round(valor_deducao*100),
            str(codigo_atividade).zfill(5),
            str(tipo_cpfcnpj),
            str(cnpj_cpf).zfill(14)
            )
        rps['assinatura'] = assinatura

        nfse = {
            'cidade': empresa.cidade,
            'cpf_cnpj': empresa.cnpj_cpf,
            'remetente': empresa.razao_social,
            'transacao': '',
            'data_inicio': self.data_emissao,
            'data_fim': self.data_emissao,
            'total_rps': '1',
            'total_servicos': str("%.2f" % self.vr_nf),
            'total_deducoes': '0',
            'lote_id': '%s' % self.id,
            'lista_rps': [rps]
        }
        return nfse
