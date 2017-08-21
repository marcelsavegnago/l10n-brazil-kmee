# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

import os
import logging
import base64
import re
import tempfile
from datetime import datetime
from decimal import Decimal


from odoo import api, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_br_base.constante_tributaria import *

_logger = logging.getLogger(__name__)

try:
    from pysped.nfe.leiaute import *

    from pybrasil.inscricao import (
        formata_cnpj, formata_cpf, limpa_formatacao
    )

    from pybrasil.data import (parse_datetime, UTC, data_hora_horario_brasilia,
                               agora)
    from pybrasil.valor import formata_valor
    from pybrasil.valor.decimal import Decimal as D
    from pybrasil.template import TemplateBrasil

except (ImportError, IOError) as err:
    _logger.debug(err)


class SpedDocumentoImport(models.TransientModel):
    _name = b'sped.documento.import'

    #
    # Os campos de anexos abaixo servem para que os anexos não possam
    # ser excluídos pelo usuário, somente através do sistema ou pelo
    # suporte
    #
    arquivo_xml_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='XML',
        ondelete='restrict',
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ]
    )
    nfe_id = fields.Many2one(
        comodel_name='sped.documento',
        string=u'NF-e',
        ondelete='set null',
    )
    edoc_input = fields.Binary(
        string=u'Arquivo do documento eletrônico',
        help=u'Somente arquivos no formato TXT e XML'
    )
    file_name = fields.Char('File Name', size=128)
    create_partner = fields.Boolean(
        string=u'Criar fornecedor automaticamente?',
        default=True,
        help=u'Cria o fornecedor automaticamente caso não esteja cadastrado'
    )
    supplier_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string=u"Parceiro",
    )

    def parse_edoc(self, filebuffer):
        filebuffer = base64.standard_b64decode(filebuffer)
        edoc_file = tempfile.NamedTemporaryFile()
        edoc_file.write(filebuffer)
        edoc_file.flush()

        nfe = NFe_310()
        nfe.set_xml(edoc_file.name)

        return nfe

    def __init__(self, pool, cr):
        super(SpedDocumentoImport, self).__init__(pool, cr)
        self.nfe = None
        self.nfref = None
        self.det = None
        self.dup = None
        self.env = None

    def importa_xml(self):
        self.nfe = self.parse_edoc(self.edoc_input)
        # TODO Buscar o protocolo da nota
        protNFe = consrecinfe_310.ProtNFe()
        nfref = NFRef_310()
        nfref.xml = self.nfe.xml
        self.nfref = nfref
        self.dup = Dup_310()
        self.dup.xml = self.nfe.xml
        vals = {}

        participantes = self.get_participantes()
        identificacao = self.get_identificacao()
        duplicatas = self.get_duplicatas()
        # itens = self.get_itens()

        vals.update(participantes)
        vals.update(identificacao)
        vals['duplicatas_ids'] = duplicatas

        result = self.env['sped.documento'].create(vals)

        return result

    def get_participantes(self):
        """
        Define quem são os participantes e se o documento é de emissão própria
        ou de terceiros
        :return: 
        """
        def search_participante(model, valor):
            return self.env[model].search([('cnpj_cpf', '=', valor)], limit=1)

        if self.nfe.infNFe.emit.CNPJ.valor:
            emit_cnpj_cpf = formata_cnpj(self.nfe.infNFe.emit.CNPJ.valor)
        elif self.nfe.infNFe.emit.CPF.valor:
            emit_cnpj_cpf = formata_cpf(self.nfe.infNFe.emit.CPF.valor)

        if self.nfe.infNFe.dest.CNPJ.valor:
            dest_cnpj_cpf = formata_cnpj(self.nfe.infNFe.dest.CNPJ.valor)
        elif self.nfe.infNFe.dest.CPF.valor:
            dest_cnpj_cpf = formata_cpf(self.nfe.infNFe.dest.CPF.valor)

        empresa = search_participante('sped.empresa', emit_cnpj_cpf) or \
                  search_participante('sped.empresa', dest_cnpj_cpf)

        if emit_cnpj_cpf == empresa.cnpj_cpf:
            partic_cnpj_cpf = dest_cnpj_cpf
            emissao = TIPO_EMISSAO_PROPRIA
        else:
            partic_cnpj_cpf = emit_cnpj_cpf
            emissao = TIPO_EMISSAO_TERCEIROS

        partic = search_participante('sped.participante', partic_cnpj_cpf)

        return {'empresa_id': empresa.id,
                'participante_id': partic.id,
                'emissao': emissao,
                }

    def get_identificacao(self):
        identificacao = {}
        identificacao['modelo'] = self.nfe.infNFe.ide.mod.valor
        identificacao['data_hora_emissao'] = self.nfe.infNFe.ide.dhEmi.valor
        identificacao['serie'] = self.nfe.infNFe.ide.serie.valor
        identificacao['numero'] = self.nfe.infNFe.ide.nNF.valor
        identificacao['entrada_saida'] = str(self.nfe.infNFe.ide.tpNF.valor)
        identificacao['ambiente_nfe'] = str(self.nfe.infNFe.ide.tpAmb.valor)
        identificacao['ind_forma_pagamento'] = str(
            self.nfe.infNFe.ide.indPag.valor)
        identificacao['finalidade_nfe'] = str(self.nfe.infNFe.ide.finNFe.valor)
        identificacao['consumidor_final'] = str(
            self.nfe.infNFe.ide.indFinal.valor)
        identificacao['presenca_comprador'] = str(
            self.nfe.infNFe.ide.indPres.valor)
        identificacao['chave'] = str(self.nfe.infNFe.Id.valor)

        domain_municipio = [
            ('codigo_ibge', '=', self.nfe.infNFe.ide.cMunFG.valor)]
        identificacao['municipio_fato_gerador_id'] = \
            self.env['sped.municipio'].search(domain_municipio)

        # Falta encontrar a operacao_id que condiz com a nota
        # nat_op = self.nfe.infNFe.ide.natOp.valor
        # identificacao['natureza_operacao_id'] = self
        # identificacao['operacao_id'] = self

        # todo: campos abaixo do campo chave no arquivo sped_documento

        return identificacao

    def get_duplicatas(self):
        dups = []
        for dup in self.nfe.infNFe.cobr.dup:
            dups.append(
                (0, 0, {
                    'numero': dup.nDup.valor,
                    'data_vencimento': dup.dVenc.valor,
                    'valor': dup.vDup.valor,
                })
            )
        return dups

    def get_itens(self):
        sped_prod = self.env['sped.produto']
        sped_doc_item = self.env['sped.documento.item']
        itens = []

        for item in self.nfe.infNFe.det:
            novo_item = {}
            produto = sped_prod.search(
                ['|', '|',
                 ('codigo', '=', item.prod.cProd.valor),
                 ('nome', '=', item.prod.xProd.valor),
                 ('codigo_barras', '=', item.prod.cEAN.valor),
                 ])
            if produto:
                novo_item.update({'produto_id': produto.id})
            else:
                novo_item.update(
                    {'produto_id': (0, 0, {
                        'codigo': item.prod.cProd.valor,
                        'nome': item.prod.xProd.valor,
                        'codigo_barras': item.prod.cEAN.valor,
                        'ncm_id': self.env['sped.ncm'].search(
                            [('codigo', '=', item.prod.NCM.valor)],
                            limit=1).id,
                        'preco_custo': item.prod.vUnCom})})

            novo_item.update(
                {
                'unidade_id': self.env['sped.unidade'].search(
                    [('codigo', '=', item.prod.uCom.valor)]
                ).id,
                'cfop_id': self.env['sped.cfop'].search(
                    [('codigo', '=', item.prod.CFOP.valor)]
                ),
                'quantidade': item.prod.qCom.valor,
                'vr_produtos': item.prod.vProd.valor,
                'vr_frete': item.prod.vFrete.valor,
                'vr_seguro': item.prod.vSeg.valor,
                'vr_outras': item.prod.vOutro.valor,
                'vr_desconto': item.prod.vDesc.valor,
                'numero_pedido': item.prod.xPed.valor,
                'numero_item_pedido': item.prod.nItemPed.valor,
                'compoe_total': item.prod.indTot.valor,
                # 'declaracao_ids': item.prod.indTot.valor,
                'vr_ibpt': item.prod.vTotTrib.valor,
                # 'documento_id.regime_tributario': item.imposto.ICMS.regime_tributario.valor,
                'org_icms': item.imposto.ICMS.orig.valor,
                'cst_icms': item.imposto.ICMS.CST.valor,
                'cst_icms_sn': item.imposto.ICMS.CSOSN.valor,
                'al_icms_sn': item.imposto.ICMS.pCredSN.valor,
                'vr_icms_sn': item.imposto.ICMS.vCredICMSSN.valor,
                'md_icms_proprio': item.imposto.ICMS.modBC.valor,
                'rd_icms_proprio': item.imposto.ICMS.pRedBC.valor,
                'bc_icms_proprio': item.imposto.ICMS.vBC.valor,
                'al_icms_proprio': item.imposto.ICMS.pICMS.valor,
                'vr_icms_proprio': item.imposto.ICMS.vICMS.valor,
                'md_icms_st': item.imposto.ICMS.modBCST.valor,
                'pr_icms_st': item.imposto.ICMS.pMVAST.valor,
                'rd_icms_st': item.imposto.ICMS.pRedBCST.valor,
                'bc_icms_st': item.imposto.ICMS.vBCST.valor,
                'al_icms_st': item.imposto.ICMS.pICMSST.valor,
                'vr_icms_st': item.imposto.ICMS.vICMSST.valor,
                'cst_pis': item.imposto.PIS.CST.valor,
                'bc_pis_proprio': item.imposto.PIS.vBC.valor,
                'al_pis_proprio': item.imposto.PIS.pPIS.valor,
            }
        )
        return itens
