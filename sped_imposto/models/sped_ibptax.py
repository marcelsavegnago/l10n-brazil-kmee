# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

import logging
import os
import requests
from odoo.addons.l10n_br_base.models.sped_base import SpedBase
from odoo import api, fields, models


_logger = logging.getLogger(__name__)

try:
    from pybrasil.data import parse_datetime
    from pybrasil.valor.decimal import Decimal as D
    from pybrasil.inscricao import limpa_formatacao

except (ImportError, IOError) as err:
    _logger.debug(err)


class SpedIBPTax(models.Model):
    _name = b'sped.ibptax'
    _description = 'IBPTax'
    _order = 'estado_id'
    _rec_name = 'estado_id'

    estado_id = fields.Many2one(
        comodel_name='sped.estado',
        string='Estado',
    )
    versao = fields.Char(
        string='Versão',
        size=20,
    )
    data_validade = fields.Date(
        string='Válida até',
    )
    ncm_ids = fields.One2many(
        comodel_name='sped.ibptax.ncm',
        inverse_name='ibptax_id',
        string='NCMs',
    )
    nbs_ids = fields.One2many(
        comodel_name='sped.ibptax.nbs',
        inverse_name='ibptax_id',
        string='NBSs',
    )
    servico_ids = fields.One2many(
        comodel_name='sped.ibptax.servico',
        inverse_name='ibptax_id',
        string='Serviços',
    )

    def _compute_webservice_liberado(self):
        for ibpt in self:
            if self.env.user.company_id.sped_empresa_id and \
                    self.env.user.company_id.sped_empresa_id.token_ibpt:
                ibpt.webservice_liberado = True
            else:
                ibpt.webservice_liberado = False

    @api.multi
    def atualizar_tabela_local(self):
        self.ensure_one()

        local_dir = os.path.dirname(__file__)
        local_dir = os.path.join(local_dir, '../data/ibpt/')

        sped_ncm = self.env['sped.ncm']
        sped_nbs = self.env['sped.nbs']
        sped_servico = self.env['sped.servico']
        sped_icms = self.env['sped.aliquota.icms.proprio']
        ibptax_ncm = self.env['sped.ibptax.ncm']
        ibptax_nbs = self.env['sped.ibptax.nbs']
        ibptax_servico = self.env['sped.ibptax.servico']

        versao = '17.2.A'
        arquivo = local_dir + 'TabelaIBPTax{uf}{versao}.csv'.format(
                uf=self.estado_id.uf, versao=versao)

        ncm_ids = ibptax_ncm.search([('ibptax_id', '=', self.id)])
        ncm_ids.unlink()

        nbs_ids = ibptax_nbs.search([('ibptax_id', '=', self.id)])
        nbs_ids.unlink()

        servico_ids = ibptax_servico.search([('ibptax_id', '=', self.id)])
        servico_ids.unlink()

        arq = open(arquivo, 'r')

        for linha in arq.readlines():
            codigo, ex, tipo, descricao, nacionalfederal, importadosfederal, \
                estadual, municipal, vigenciainicio, vigenciafim, chave, \
                versao, fonte = linha.decode('iso-8859-1').split(';')

            if descricao[0] == '"':
                descricao = descricao[1:]

            if descricao[-1] == '"':
                descricao = descricao[0:-1]

            if tipo == '0':
                ncm_ids = sped_ncm.search(
                    [('codigo', '=', codigo), ('ex', '=', ex)])

                if len(ncm_ids) == 0:
                    dados = {
                        'codigo': codigo,
                        'ex': ex,
                        'descricao': descricao,
                    }
                    ncm_ids = sped_ncm.create(dados)

                icms_ids = sped_icms.search([('al_icms', '=', D(estadual))])

                dados = {
                    'ibptax_id': self.id,
                    'ncm_id': ncm_ids[0].id,
                    'al_ibpt_nacional': D(nacionalfederal),
                    'al_ibpt_internacional': D(importadosfederal),
                    'al_ibpt_estadual': D(estadual),
                    'al_icms_id': icms_ids[0].id if len(icms_ids) else False,
                }
                ibptax_ncm.create(dados)

            elif tipo == '1':
                nbs_ids = sped_nbs.search([('codigo', '=', codigo)])

                if len(nbs_ids) == 0:
                    dados = {
                        'codigo': codigo,
                        'descricao': descricao,
                    }
                    nbs_ids = sped_nbs.create(dados)

                dados = {
                    'ibptax_id': self.id,
                    'nbs_id': nbs_ids[0].id,
                    'al_ibpt_nacional': D(nacionalfederal),
                    'al_ibpt_internacional': D(importadosfederal),
                    'al_ibpt_municipal': D(municipal),
                }
                ibptax_nbs.create(dados)

            elif tipo == '2' and descricao != 'Vetado':
                servico_ids = sped_servico.search([('codigo', '=', codigo)])

                if len(servico_ids) == 0:
                    dados = {
                        'codigo': codigo,
                        'descricao': descricao,
                    }
                    servico_ids = sped_servico.create(dados)

                dados = {
                    'ibptax_id': self.id,
                    'servico_id': servico_ids[0].id,
                    'al_ibpt_nacional': D(nacionalfederal),
                    'al_ibpt_internacional': D(importadosfederal),
                    'al_ibpt_municipal': D(municipal),
                }
                ibptax_servico.create(dados)

        arq.close()
        self.data_validade = str(parse_datetime(vigenciafim))[:10]
        self.versao = versao

    def atualizar_tabela_webservice(self):
        self.ensure_one()
        self._atualizar_tabela_webservice_ncm()
        self._atualizar_tabela_webservice_nbs()
        self._atualizar_tabela_webservice_servico()

    def _atualizar_tabela_webservice_ncm(self):
        self.ensure_one()

        sped_icms = self.env['sped.aliquota.icms.proprio']
        ibptax_ncm = self.env['sped.ibptax.ncm']

        ncm_ids = self.env['sped.ncm'].search([])
        versao = self.versao
        data_validade = self.data_validade
        for ncm in ncm_ids:
            resposta = self.consulta_ibpt_produto(ncm.codigo,ex=ncm.ex)

            if resposta is None:
                continue

            nacionalfederal = resposta['Nacional']
            estadual = resposta['Estadual']
            importadosfederal = resposta['Importado']
            versao = resposta['Versao']
            data_validade = parse_datetime(resposta['VigenciaFim']).date()

            icms_ids = sped_icms.search([('al_icms', '=', D(estadual))])

            dados = {
                'ibptax_id': self.id,
                'ncm_id': ncm.id,
                'al_ibpt_nacional': D(nacionalfederal),
                'al_ibpt_internacional': D(importadosfederal),
                'al_ibpt_estadual': D(estadual),
                'al_icms_id': icms_ids[0].id if len(icms_ids) else False,
            }
            ibptax_ncm.create(dados)

        self.versao = versao
        self.data_validade = str(data_validade)

    def _atualizar_tabela_webservice_nbs(self):
        self.ensure_one()

        ibptax_nbs = self.env['sped.ibptax.nbs']

        nbs_ids = self.env['sped.nbs'].search([])
        versao = self.versao
        data_validade = self.data_validade
        for nbs in nbs_ids:
            resposta = self.consulta_ibpt_servico(nbs.codigo)

            if resposta is None:
                continue

            nacionalfederal = resposta['Nacional']
            municipal = resposta['Municipal']
            importadosfederal = resposta['Importado']
            versao = resposta['Versao']
            data_validade = parse_datetime(resposta['VigenciaFim']).date()

            dados = {
                'ibptax_id': self.id,
                'nbs_id': nbs.id,
                'al_ibpt_nacional': D(nacionalfederal),
                'al_ibpt_internacional': D(importadosfederal),
                'al_ibpt_municipal': D(municipal),
            }
            ibptax_nbs.create(dados)

        self.versao = versao
        self.data_validade = str(data_validade)

    def _atualizar_tabela_webservice_servico(self):
        self.ensure_one()

        ibptax_servico = self.env['sped.ibptax.servico']

        servico_ids = self.env['sped.servico'].search([])
        versao = self.versao
        data_validade = self.data_validade
        for servico in servico_ids:
            resposta = self.consulta_ibpt_servico(servico.codigo)

            if resposta is None:
                continue

            nacionalfederal = resposta['Nacional']
            municipal = resposta['Municipal']
            importadosfederal = resposta['Importado']
            versao = resposta['Versao']
            data_validade = parse_datetime(resposta['VigenciaFim']).date()

            dados = {
                'ibptax_id': self.id,
                'servico_id': servico.id,
                'al_ibpt_nacional': D(nacionalfederal),
                'al_ibpt_internacional': D(importadosfederal),
                'al_ibpt_municipal': D(municipal),
            }
            ibptax_servico.create(dados)

        self.versao = versao
        self.data_validade = str(data_validade)

    def _consulta_ibpt_webservice(self, tipo, dados):
        self.ensure_one()
        empresa = self.env.user.company_id.sped_empresa_id
        url = b'http://iws.ibpt.org.br/api/deolhonoimposto/{tipo}'.format(tipo=tipo)

        envio = {
            b'token': empresa.token_ibpt,
            b'cnpj': limpa_formatacao(empresa.cnpj_cpf),
            b'uf': self.estado_id.uf,
        }

        #
        # Não tenho ideia do porquê, mas um simples envio.update(dados)
        # resulta em envio == None...
        #
        # envio = envio.update(dados)
        for chave in dados.keys():
            if dados[chave] is None:
                continue

            envio[chave] = dados[chave]

        response = requests.get(url, params=envio)

        #
        # 404 quer dizer que o NCM/Serviço/NBS não foi encontrado; tudo bem
        # tem empresa que usa NCM que não existe mesmo, por enquanto, pelo
        # menos...
        #
        if response.status_code != 200:
            if response.status_code == 404:
                response = None
            else:
                raise response.text

        else:
            response = response.json()

        return response

    def consulta_ibpt_produto(self, ncm, ex='', codigo_produto=None,
            descricao_produto=None, unidade_medida=None, valor_produto=None,
            codigo_barras_produto=None):
        self.ensure_one()
        dados = {
            b'codigo': ncm,
            b'ex': ex or '0',
            b'codigoInterno': codigo_produto,
            b'descricao': descricao_produto,
            b'unidadeMedida': unidade_medida,
            b'valor': valor_produto,
            b'gtin': codigo_barras_produto,
        }

        resposta = self._consulta_ibpt_webservice('Produtos', dados)

        return resposta

    def consulta_ibpt_servico(self, servico_nbs, descricao_servico=None,
            unidade_medida=None, valor_servico=None):
        self.ensure_one()
        dados = {
            b'codigo': servico_nbs,
            b'descricao': descricao_servico,
            b'unidadeMedida': unidade_medida,
            b'valor': valor_servico,
        }

        resposta = self._consulta_ibpt_webservice('Servicos', dados)

        return resposta


class SpedIBPTaxNCM(SpedBase, models.Model):
    _name = b'sped.ibptax.ncm'
    _description = 'IBPTax por NCM'

    ibptax_id = fields.Many2one(
        comodel_name='sped.ibptax',
        string='IBPTax',
        ondelete='cascade',
    )
    estado_id = fields.Many2one(
        comodel_name='sped.estado',
        string='Estado',
        related='ibptax_id.estado_id',
        store=True,
    )
    ncm_id = fields.Many2one(
        comodel_name='sped.ncm',
        string='NCM',
    )
    al_ibpt_nacional = fields.Monetary(
        string='Nacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_internacional = fields.Monetary(
        string='Internacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_estadual = fields.Monetary(
        string='Estadual',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_icms_id = fields.Many2one(
        comodel_name='sped.aliquota.icms.proprio',
        string='Estadual',
    )


class SpedIBPTaxNBS(SpedBase, models.Model):
    _name = b'sped.ibptax.nbs'
    _description = 'IBPTax por NBS'

    ibptax_id = fields.Many2one(
        comodel_name='sped.ibptax',
        string='IBPTax',
        ondelete='cascade',
    )
    estado_id = fields.Many2one(
        comodel_name='sped.estado',
        string='Estado',
        related='ibptax_id.estado_id',
        store=True,
    )
    nbs_id = fields.Many2one(
        comodel_name='sped.nbs',
        string='NBS',
    )
    al_ibpt_nacional = fields.Monetary(
        string='Nacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_internacional = fields.Monetary(
        string='Internacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_municipal = fields.Monetary(
        string='Municipal',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )


class SpedIBPTaxServico(SpedBase, models.Model):
    _name = b'sped.ibptax.servico'
    _description = 'IBPTax por Serviço'

    ibptax_id = fields.Many2one(
        comodel_name='sped.ibptax',
        string='IBPTax',
        ondelete='cascade',
    )
    estado_id = fields.Many2one(
        comodel_name='sped.estado',
        string='Estado',
        related='ibptax_id.estado_id',
        store=True,
    )
    servico_id = fields.Many2one(
        comodel_name='sped.servico',
        string='Serviço',
    )
    al_ibpt_nacional = fields.Monetary(
        string='Nacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_internacional = fields.Monetary(
        string='Internacional',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
    al_ibpt_municipal = fields.Monetary(
        string='Municipal',
        digits=(5, 2),
        currency_field='currency_aliquota_id',
    )
