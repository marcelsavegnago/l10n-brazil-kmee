# -*- coding: utf-8 -*-
#
# Geração do arquivo do SPED Fiscal
#

from __future__ import division, print_function, unicode_literals

import os
import StringIO
from pybrasil.data import hoje, parse_datetime, data_hora_horario_brasilia
from pybrasil.valor.decimal import Decimal as D
from copy import copy
from pybrasil.inscricao import limpa_formatacao
from osv import osv, fields
from pybrasil.valor import formata_valor
from sped.constante_tributaria import *
from sped.models.sped_calcula_impostos import calcula_item
from time import time
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import datetime


#
# Listas de modelos fiscais para o SPED
#
MODELO_FISCAL_SPED_NF = (
    b'01',
    b'1B',
    b'04',
    b'55',
)

MODELO_FISCAL_SPED_ENERGIA = (
    b'06',
    b'29',
    b'28',
)

MODELO_FISCAL_SPED_TELEFONE = (
    b'21',
    b'22',
)

MODELO_FISCAL_SPED_TRANSPORTE = (
    b'07',
    b'08',
    b'8B',
    b'09',
    b'10',
    b'11',
    b'26',
    b'27',
    b'57',
)

CFOP_DEVOLUCAO = (
    #
    # Devolução entradas
    #
    b'1410', b'2410',
    b'1411', b'2411',
    b'1412', b'2412',
    # '1413', '2413' não existem
    b'1414', b'2414',
    b'1415', b'2415',
    b'1660', b'2660',
    b'1661', b'2661',
    b'1662', b'2662',
    #
    # Devolução saídas
    #
    #'5410', '6410',
    #'5411', '6411',
    #'5412', '6412',
    #'5413', '6413',
    #'5414', '6414',
    #'5415', '6415',
    #'5660', '6660',
    #'5661', '6661',
    #'6662', '6662',
)

CFOP_RESSARCIMENTO = (
    b'1603', b'2603',
    #'5603', '6603',
)

CFOP_ICMS_ST = CFOP_DEVOLUCAO + CFOP_RESSARCIMENTO


def formata_valor_sped(numero, decimais=2):
    numero = D(numero)

    if decimais:
        numero = numero.quantize(D('0.' + ''.zfill(decimais-1) + '1'))

    return formata_valor(numero, casas_decimais=decimais, separador_milhar='')


class SPEDFiscal(object):
    def __init__(self):
        self.finalidade = '0'
        self.filial = None
        self.data_inicial = hoje()
        self.data_final = hoje()
        self.perfil = 'A'
        self.tipo_atividade = '1'
        self.movimentos_blocos = {
            '0': True,
            'C': False,
            'D': False,
            'E': True,
            'G': False,
            'H': False,
            'K': False,
            '1': False,
            '9': True,
        }
        self.totais_registros = {
            'geral': 0
        }
        self.total_icms_entradas = D(0)
        self.total_icms_saidas = D(0)
        self.credito_icms = D(0)
        self.debito_icms = D(0)
        self.questor = False
        self.locais_estoque = []

    @property
    def versao(self):
        if self.data_inicial >= datetime.date(2016, 1, 1):
            return '010'

        return '009'

    def gera_arquivo(self, nome_arquivo=''):
        #self._arq = file(nome_arquivo, 'w')
        self._arq = StringIO.StringIO()

        #
        # Abertura do arquivo
        #
        self.registro_0000()
        #
        # Bloco 0
        #
        self.registro_inicial_bloco('0')
        self.registro_0005()  # Fantasia e contatos (telefone e email)
        #self.registro_0015()  # Inscrições em outros estados
        #self.registro_0100()  # Contador
        self.registro_0150()
        self.registro_0190()
        self.registro_0200()
        self.registro_0400()
        ##self.registro_0460()
        self.registro_final_bloco('0')

        #
        # Bloco C
        #
        self.registro_inicial_bloco('C')
        self.registro_C100()
        self.registro_C500()
        self.registro_final_bloco('C')

        #
        # Bloco D
        #
        self.registro_inicial_bloco('D')
        self.registro_D100()
        self.registro_D500()
        self.registro_final_bloco('D')

        #
        # Bloco E
        #
        self.registro_inicial_bloco('E')
        self.registro_E100()
        #self.registro_E500()
        self.registro_final_bloco('E')

        #
        # Bloco G
        #
        self.registro_inicial_bloco('G')
        self.registro_final_bloco('G')

        #
        # Bloco H
        #
        self.registro_inicial_bloco('H')
        self.registro_H005()
        self.registro_final_bloco('H')

        #
        # Bloco K
        #
        self.registro_inicial_bloco('K')
        self.registro_final_bloco('K')

        #
        # Bloco 1
        #
        self.registro_inicial_bloco('1')
        self.registro_final_bloco('1')

        #
        # Bloco 9
        #
        self.registro_inicial_bloco('9')
        self.registro_9900()
        self.registro_final_bloco('9')

        #
        # Encerramento do arquivo
        #
        self.registro_9999()

        self.arquivo = self._arq.getvalue()

        self._arq.close()

    def _grava_registro(self, registro):
        r = registro
        registro = registro.replace('“', '"')
        registro = registro.replace('”', '"')
        registro = registro.replace('‘', "'")
        registro = registro.replace('’', "'")

        if r != registro:
            print(registro)
        #self._arq.write(registro.encode('iso-8859-1'))
        self._arq.write(registro.encode('utf-8'))

    def registro_inicial_bloco(self, bloco):
        self.totais_registros['geral'] += 1
        self.totais_registros[bloco + '001'] = 1

        reg = '|' + bloco + '001'

        if self.movimentos_blocos[bloco]:
            reg += '|0'
        else:
            reg += '|1'

        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_final_bloco(self, bloco):
        self.totais_registros['geral'] += 1
        self.totais_registros[bloco + '990'] = 1

        reg = '|' + bloco + '990'

        total = 0
        for tipo_registro, quantidade in self.totais_registros.iteritems():
            if tipo_registro[0] == bloco:
                total += quantidade

        reg += '|' + unicode(total)
        reg += '|\r\n'
        self._grava_registro(reg)

    def _busca_ids(self, sql, dados={}, varios_campos=False):
        dados_sql = {
            'cnpj': self.filial_a_gerar.cnpj_cpf,
            'data_inicial': self.data_inicial.strftime('%Y-%m-%d'),
            'data_final': self.data_final.strftime('%Y-%m-%d'),
            'MODELO_FISCAL_SPED_NF': MODELO_FISCAL_SPED_NF,
            'MODELO_FISCAL_SPED_TRANSPORTE': MODELO_FISCAL_SPED_TRANSPORTE,
            'MODELO_FISCAL_SPED_ENERGIA': MODELO_FISCAL_SPED_ENERGIA,
            'MODELO_FISCAL_SPED_TELEFONE': MODELO_FISCAL_SPED_TELEFONE,
            'CFOP_DEVOLUCAO': CFOP_DEVOLUCAO,
            'CFOP_RESSARCIMENTO': CFOP_RESSARCIMENTO,
            'CFOP_ICMS_ST': CFOP_ICMS_ST,
        }
        dados_sql.update(dados)
        sql_gerar = sql.format(**dados_sql)
        sql_gerar = sql_gerar.replace(', )', ')')
        sql_gerar = sql_gerar.replace(',)', ')')

        print(sql_gerar)

        self.cr.execute(sql_gerar)

        dados = self.cr.fetchall()
        ids = []

        if not varios_campos:
            for id, in dados:
                if id not in ids:
                    ids.append(id)
        else:
            ids = dados

        return ids

    #
    # Bloco 0
    # Abertura, identificação e referências
    #
    def registro_0000(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['0000'] = 1
        self.filial_a_gerar = self.filial
        self.prepara_ids()

        #
        # Determina o tipo de atividade baseado no fato de haver ou não registros com IPI
        #
        #self.doc_ipi = self.notasfiscais.filter(
            #Q(situacao__in=models.SITUACAO_FISCAL_SPED_CONSIDERA_ATIVO),
            #~Q(notafiscalitem__cst_ipi__in=('XX', '', None)))

        ##self.doc_ipi = self.notasfiscais.filter(situacao__in=models.SITUACAO_FISCAL_SPED_CONSIDERA_ATIVO).extra(
            ##where=['("fis_notafiscal"."id" IN (select nfi.notafiscal_id from fis_notafiscalitem nfi where nfi.cst_ipi not in (\'XX\', \'\')))']
        ##)
        ##self.doc_ipi_rezumo = self.notasfiscais.filter(situacao__in=models.SITUACAO_FISCAL_SPED_CONSIDERA_ATIVO).extra(
            ##where=['("u0"."id" IN (select nfi.notafiscal_id from fis_notafiscalitem nfi where nfi.cst_ipi not in (\'XX\', \'\')))']
        ##)

        ##if self.doc_ipi.count() == 0:
            ##self.tipo_atividade = '1'
        ##else:
            ##self.tipo_atividade = '0'

        reg = '|0000'
        reg += '|' + self.versao
        reg += '|' + self.finalidade
        reg += '|' + self.data_inicial.strftime('%d%m%Y')
        reg += '|' + self.data_final.strftime('%d%m%Y')
        reg += '|' + self.filial.razao_social.strip()

        #
        # CNPJ ou CPF
        #
        if len(self.filial.cnpj_cpf) == 18:
            reg += '|' + limpa_formatacao(self.filial.cnpj_cpf)
            reg += '|'
        else:
            reg += '|'
            reg += '|' + limpa_formatacao(self.filial.cnpj_cpf)

        reg += '|' + self.filial.estado
        reg += '|' + limpa_formatacao(self.filial.ie or '').strip()
        reg += '|' + self.filial.municipio_id.codigo_ibge[:7]
        reg += '|' + limpa_formatacao(self.filial.im or '').strip()
        reg += '|' + limpa_formatacao(self.filial.suframa or '').strip()
        reg += '|' + self.perfil
        reg += '|' + self.tipo_atividade
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_0005(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['0005'] = 1

        reg = '|0005'
        reg += '|' + self.filial.fantasia.strip()
        reg += '|' + limpa_formatacao(self.filial.cep.strip())
        reg += '|' + self.filial.endereco.strip()
        reg += '|' + self.filial.numero.strip()
        reg += '|' + (self.filial.complemento or '')
        reg += '|' + (self.filial.bairro or '')
        reg += '|' + limpa_formatacao(self.filial.fone or '').strip()
        reg += '|' + limpa_formatacao(self.filial.fone or '').strip()
        reg += '|' + limpa_formatacao(self.filial.email_nfe or '').strip()
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_0015(self):
        return ''

        if not self.filial.participanteie_set.count():
            return ''

        self.totais_registros['0015'] = 0

        for ie in self.filial.participanteie_set.all():
            self.totais_registros['geral'] += 1
            self.totais_registros['0015'] += 1
            reg = '|0015'
            reg += '|' + ie.estado
            reg += '|' + ie.ie.strip()
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_0100(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['0100'] = 1
        contador = Contabilista.objects.get(pk=1)

        reg = '|0100'
        reg += '|' + contador.nome.strip()

        if len(contador.cnpj_cpf) == 11:
            reg += '|' + contador.cnpj_cpf.strip()
        else:
            reg += '|'

        reg += '|' + contador.crc.strip()

        if len(contador.cnpj_cpf) == 14:
            reg += '|' + contador.cnpj_cpf.strip()
        else:
            reg += '|'

        reg += '|' + contador.cep.strip()
        reg += '|' + contador.endereco.strip()
        reg += '|' + contador.numero.strip()
        reg += '|' + contador.complemento.strip()
        reg += '|' + contador.bairro.strip()
        reg += '|' + contador.fone.strip()
        reg += '|' + contador.fax.strip()
        reg += '|' + contador.emeio.strip()
        reg += '|' + contador.municipio.ibge()
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_0150(self):
        if len(self.participante_ids) == 0:
            return ''

        self.totais_registros['0150'] = 0
        partner_pool = self.filial.pool.get('res.partner')

        ja_foi = []
        for participante in partner_pool.browse(self.cr, 1, self.participante_ids):
            if participante.cnpj_cpf in ja_foi:
                continue

            ja_foi.append(participante.cnpj_cpf)
            self.totais_registros['geral'] += 1
            self.totais_registros['0150'] += 1
            reg = '|0150'

            #
            # Código é o CNPJ
            #
            if not participante.cnpj_cpf:
                raise Exception(u'Erro!', u'Cliente ou fornecedor sem CNPJ/CPF: "%s"' % participante.name)

            reg += '|' + limpa_formatacao(participante.cnpj_cpf)

            if participante.razao_social:
                reg += '|' + participante.razao_social.strip()
            else:
                reg += '|' + participante.name.strip()

            try:
                reg += '|' + participante.municipio_id.pais_id.codigo_bacen
            except:
                reg += '|1058'

            if participante.cnpj_cpf[:2] == 'EX':
                reg += '|'
                reg += '|'
            else:
                if len(participante.cnpj_cpf) == 18:
                    reg += '|' + limpa_formatacao(participante.cnpj_cpf)
                    reg += '|'
                else:
                    reg += '|'
                    reg += '|' + limpa_formatacao(participante.cnpj_cpf)

            if participante.ie == 'ISENTO' or participante.contribuinte in ['2', '3']:
                reg += '|'
            else:
                reg += '|' + limpa_formatacao(participante.ie or '').strip()

            try:
                reg += '|' + participante.municipio_id.codigo_ibge[:7]
            except:
                reg += '|'

            reg += '|' + limpa_formatacao(participante.suframa or '').strip()
            reg += '|' + (participante.endereco or '').strip()
            reg += '|' + (participante.numero or '').strip()
            reg += '|' + (participante.complemento or '').strip()
            reg += '|' + (participante.bairro or '').strip()
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_0190(self):
        self.totais_registros['0190'] = 0

        unidade_pool = self.filial.pool.get('product.uom')
        ja_foi = []

        for unidade in unidade_pool.browse(self.cr, 1, self.unidade_ids):
            if unidade.id in ja_foi:
                continue

            ja_foi.append(unidade.id)
            self.totais_registros['geral'] += 1
            self.totais_registros['0190'] += 1
            reg = '|0190'

            if self.questor:
                reg += '|' + unidade.name or ''
            else:
                reg += '|' + str(unidade.id)

            reg += '|' + unidade.name or ''
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_0200(self):
        self.totais_registros['0200'] = 0

        product_pool = self.filial.pool.get('product.product')
        ja_foi = []

        for produto in product_pool.browse(self.cr, 1, self.produto_ids):
            if produto.id in ja_foi:
                continue

            ja_foi.append(produto.id)
            self.totais_registros['geral'] += 1
            self.totais_registros['0200'] += 1
            reg = '|0200'
            reg += '|' + (produto.default_code or '')
            reg += '|' + produto.name
            reg += '|' + (produto.ean13 or '')
            reg += '|'

            if self.questor:
                reg += '|' + produto.uom_id.name or ''
            else:
                reg += '|' + str(produto.uom_id.id)

            reg += '|' + (produto.tipo or '00')
            if produto.ncm_id:
                reg += '|' + produto.ncm_id.codigo
                reg += '|' + (produto.ncm_id.ex or '')
                reg += '|' + produto.ncm_id.codigo[0:2]
            else:
                reg += '|'
                reg += '|'
                reg += '|'

            if produto.servico_id:
                reg += '|' + produto.servico_id.codigo
            else:
                reg += '|'

            ### Busca a alíquota do ICMS nos itens da família tributária
            ##fam_itens = produto.familiatributaria.familiatributariaitem_set.filter(estado_origem=self.filial.municipio.estado,
            ##    estado_destino=self.filial.municipio.estado,
            ##    data_inicio__lte=self.data_final.strftime('%Y-%m-%d')).order_by('-data_inicio')
            ##
            ##if fam_itens.count():
            ##    reg += '|' + formata_valor_sped(fam_itens[0].icms_proprio.al_icms)
            ##else:
            ##    reg += '|'
            reg += '|18,00'

            reg += '|\r\n'
            self._grava_registro(reg)

            #self.registro_0206(produto)

    def registro_0206(self, produto):
        try:
            if not produto.produtocombustivel:
                return ''
        except:
            return ''

        self.totais_registros['geral'] += 1

        if '0206' in self.totais_registros.keys():
            self.totais_registros['0206'] += 1
        else:
            self.totais_registros['0206'] = 1

        reg = '|0206'
        reg += '|' + produto.produtocombustivel.codigo_anp.strip()
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_0400(self):
        self.totais_registros['0400'] = 0

        natureza_pool = self.filial.pool.get('sped.naturezaoperacao')
        ja_foi = []

        for natureza in natureza_pool.browse(self.cr, 1, self.natureza_ids):
            if natureza.codigo in ja_foi:
                continue

            ja_foi.append(natureza.codigo)
            self.totais_registros['geral'] += 1
            self.totais_registros['0400'] += 1
            reg = '|0400'
            reg += '|' + natureza.codigo.strip()
            reg += '|' + natureza.nome.strip()
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_0460(self):
        #
        # Verifica se há notas de terceiros com ICMS_ST_RETIDO para lançar nas obs
        #
        if self.notasfiscais.filter(Q(emissao=models.TIPO_EMISSAO_TERCEIROS), ~Q(bc_icms_st_retido=0)).count() == 0:
            return ''

        self.totais_registros['0460'] = 0

        self.totais_registros['geral'] += 1
        self.totais_registros['0460'] += 1
        reg = '|0460'
        reg += '|000001'
        reg += '|ICMS RETIDO POR SUBSTITUIÇÃO TRIBUTÁRIA:'
        reg += '|\r\n'
        self._grava_registro(reg)

    #
    # Bloco C
    # Documentos Fiscais de mercadorias com ICMS e IPI
    #
    def registro_C100(self, piscofins=False):
        if len(self.bloco_c100_ids) == 0:
            return ''

        self.totais_registros['C100'] = 0

        doc_pool = self.filial.pool.get('sped.documento')

        for nf in doc_pool.browse(self.cr, 1, self.bloco_c100_ids):
            #self.ajusta_itens(nf)
            #if not self.ajusta_itens(nf):
                #continue

            #
            # Prepara um queryset para uso posterior, retirando os itens
            # que sejam relativos a serviço para a apuração de ICMS e IPI
            #
            #nf.itens_sem_servico = nf.notafiscalitem_set.exclude(produtoservico__tipo=models.TIPO_PRODUTO_SERVICO_SERVICOS).defer('infadic')

            #if nf.itens_sem_servico.count() == 0:
                #continue

            self.totais_registros['geral'] += 1
            self.totais_registros['C100'] += 1
            reg = '|C100'
            reg += '|' + nf.entrada_saida
            reg += '|' + nf.emissao

            if nf.situacao in SITUACAO_FISCAL_SPED_CONSIDERA_CANCELADO:
                reg += '|'
            else:
                reg += '|' + limpa_formatacao(nf.partner_id.cnpj_cpf)

            if nf.modelo in MODELO_FISCAL_SPED_NF:
                reg += '|' + nf.modelo
            else:
                reg += '|01'

            reg += '|' + nf.situacao
            reg += '|' + (nf.serie or '')
            reg += '|' + unicode(nf.numero)
            reg += '|' + (nf.chave or '')

            if nf.situacao in SITUACAO_FISCAL_SPED_CONSIDERA_CANCELADO:
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|\r\n'
                self._grava_registro(reg)

            else:
                if nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                else:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

                #
                # Envia a data de entrada/saída somente se o mês e ano forem
                # iguais ao mês e ano da data de emissão
                #
                if not nf.data_entrada_saida_brasilia:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')
                elif nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                elif nf.data_emissao_brasilia[:7] <= nf.data_entrada_saida_brasilia[:7]:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                else:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

                reg += '|' + formata_valor_sped(nf.vr_nf)
                reg += '|' + (nf.forma_pagamento or '9')

                reg += '|' + formata_valor_sped(nf.vr_desconto)
                reg += '|'
                reg += '|' + formata_valor_sped(nf.vr_produtos)

                #
                # Converte da modalidade do frete da NF-e para a modalidade do frete
                # do SPED
                #
                if nf.modalidade_frete == MODALIDADE_FRETE_EMITENTE:
                    reg += '|1'
                elif nf.modalidade_frete == MODALIDADE_FRETE_DESTINATARIO:
                    reg += '|2'
                elif nf.modalidade_frete == MODALIDADE_FRETE_TERCEIROS:
                    reg += '|0'
                else:
                    reg += '|9'

                reg += '|' + formata_valor_sped(nf.vr_frete)
                reg += '|' + formata_valor_sped(nf.vr_seguro)
                reg += '|' + formata_valor_sped(nf.vr_outras)
                reg += '|' + formata_valor_sped(nf.bc_icms_proprio)
                reg += '|' + formata_valor_sped(D(nf.vr_icms_proprio or 0) + D(nf.vr_icms_sn or 0))
                reg += '|' + formata_valor_sped(nf.bc_icms_st)
                reg += '|' + formata_valor_sped(nf.vr_icms_st)
                reg += '|' + formata_valor_sped(nf.vr_ipi)
                reg += '|' + formata_valor_sped(nf.vr_pis_proprio)
                reg += '|' + formata_valor_sped(nf.vr_cofins_proprio)
                reg += '|' + formata_valor_sped(nf.vr_pis_st)
                reg += '|' + formata_valor_sped(nf.vr_cofins_st)
                reg += '|\r\n'
                self._grava_registro(reg)

                #
                # Credita ou debita o ICMS próprio
                #
                if nf.situacao in [SITUACAO_FISCAL_REGULAR, SITUACAO_FISCAL_COMPLEMENTAR]:
                    if nf.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                        self.total_icms_entradas += D(nf.vr_icms_proprio)
                        #print('entrou', self.total_icms_entradas)
                    else:
                        self.total_icms_saidas += D(nf.vr_icms_proprio)
                        #print('saiu', self.total_icms_saidas)

                #
                # Itens somente para notas de terceiros
                #
                if nf.emissao == TIPO_EMISSAO_TERCEIROS or piscofins or self.questor:
                    self.registro_C170(nf)
                    #reg += self.registro_C176()

                if not piscofins:
                    self.registro_resumo(nf, 'C190')
                #reg += self.registro_C195()
                #reg += self.registro_C197()

    def registro_C170(self, nf):
        if len(nf.documentoitem_ids) == 0:
            return ''

        todos_tem_produto = True
        todos_tem_cfop = True
        for item in nf.documentoitem_ids:
            if not item.org_icms:
                item.org_icms = '0'
            if not item.cst_icms:
                item.cst_icms = '41'
            todos_tem_produto = todos_tem_produto and item.produto_id
            todos_tem_cfop = todos_tem_cfop and item.cfop_id

        if (not todos_tem_produto) or (not todos_tem_cfop):
            return ''

        if not 'C170' in self.totais_registros.keys():
            self.totais_registros['C170'] = 0

        numero_item = 0
        #
        # Usa o queryset preparado anteriormente sem os itens de serviço
        #
        for item in nf.documentoitem_ids:
            if not item.org_icms:
                item.org_icms = '0'
            if not item.cst_icms:
                item.cst_icms = '41'
            #
            # Serviços não entram aqui
            #
            #if item.produto_id.tipo == '09':
                #continue

            self.totais_registros['geral'] += 1
            self.totais_registros['C170'] += 1
            numero_item += 1
            reg = '|C170'
            reg += '|' + unicode(numero_item)
            reg += '|' + unicode(item.produto_id.default_code or '')
            reg += '|'
            reg += '|' + formata_valor_sped(item.quantidade, decimais=5)

            if item.produto_id.uom_id:
                if self.questor:
                    reg += '|' + unicode(item.produto_id.uom_id.name or '')
                else:
                    reg += '|' + unicode(item.produto_id.uom_id.id)
            else:
                reg += '|' + unicode(self.unidade_ids[0])

            reg += '|' + formata_valor_sped(item.vr_produtos)
            reg += '|' + formata_valor_sped(item.vr_desconto)

            if item.movimentacao_fisica:
                reg += '|0'
            else:
                reg += '|1'

            if nf.regime_tributario == REGIME_TRIBUTARIO_SIMPLES:
                reg += '|' + item.cst_icms_sn
            else:
                reg += '|' + item.org_icms + item.cst_icms

            reg += '|' + item.cfop_id.codigo
            try:
                reg += '|' + nf.naturezaoperacao_id.codigo
            except:
                reg += '|1'

            if item.emissao == '0' or (item.documento_id.entrada_saida == '0' and item.credita_icms_proprio):
                reg += '|' + formata_valor_sped(item.bc_icms_proprio)
                reg += '|' + formata_valor_sped(item.al_icms_proprio)
                reg += '|' + formata_valor_sped(D(item.vr_icms_proprio) + D(item.vr_icms_sn))
            else:
                reg += '|0,00'
                reg += '|0,00'
                reg += '|0,00'

            if item.emissao == '0':
                reg += '|' + formata_valor_sped(item.bc_icms_st)
                reg += '|' + formata_valor_sped(item.al_icms_st)
                reg += '|' + formata_valor_sped(item.vr_icms_st)
            else:
                reg += '|0,00'
                reg += '|0,00'
                reg += '|0,00'

            if not item.cst_ipi:
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
            else:
                reg += '|' + item.apuracao_ipi

                if item.documento_id.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                    reg += '|49'
                else:
                    reg += '|' + item.cst_ipi

                reg += '|'
                reg += '|' + formata_valor_sped(item.bc_ipi)
                reg += '|' + formata_valor_sped(item.al_ipi)
                reg += '|' + formata_valor_sped(item.vr_ipi)

            reg += '|' + item.cst_pis
            reg += '|' + formata_valor_sped(item.bc_pis_proprio)

            if (item.md_pis_proprio == MODALIDADE_BASE_PIS_ALIQUOTA) and (not item.cst_pis in ST_PIS_CALCULA_QUANTIDADE):
                reg += '|' + formata_valor_sped(item.al_pis_proprio)
                reg += '|'
                reg += '|'
            else:
                reg += '|'
                reg += '|' + formata_valor_sped(item.quantidade, decimais=3)
                reg += '|' + formata_valor_sped(item.al_pis_proprio)

            reg += '|' + formata_valor_sped(item.vr_pis_proprio)

            reg += '|' + item.cst_cofins
            reg += '|' + formata_valor_sped(item.bc_cofins_proprio)

            if (item.md_cofins_proprio == MODALIDADE_BASE_COFINS_ALIQUOTA) and (not item.cst_cofins in ST_COFINS_CALCULA_QUANTIDADE):
                reg += '|' + formata_valor_sped(item.al_cofins_proprio)
                reg += '|'
                reg += '|'
            else:
                reg += '|'
                reg += '|' + formata_valor_sped(item.quantidade, decimais=3)
                reg += '|' + formata_valor_sped(item.al_cofins_proprio)

            reg += '|' + formata_valor_sped(item.vr_cofins_proprio)

            #else:
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'
                #reg += '|'

            reg += '|'
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_C176(self):
        self.totais_registros['geral'] += 1

        if not 'C176' in self.totais_registros.keys():
            self.totais_registros['C176'] = 1
        else:
            self.totais_registros['C176'] += 1

        reg = '|C176'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_C195(self, nf):
        if (nf.emissao != TIPO_EMISSAO_TERCEIROS) or (nf.bc_icms_st_retido == 0):
            return

        self.totais_registros['geral'] += 1

        if not 'C195' in self.totais_registros.keys():
            self.totais_registros['C195'] = 1
        else:
            self.totais_registros['C195'] += 1

        reg = '|C195'
        reg += '|000001'
        reg += '|BASE DE CÁLCULO: R$ ' + formata_valor(D(nf.bc_icms_st_retido))
        reg += '; VALOR: R$ ' + formata_valor(D(nf.vr_icms_st_retido))
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_C197(self):
        self.totais_registros['geral'] += 1

        if not 'C197' in self.totais_registros.keys():
            self.totais_registros['C197'] = 1
        else:
            self.totais_registros['C197'] += 1

        reg = '|C197'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_C500(self):
        if len(self.bloco_c500_ids) == 0:
            return ''

        self.totais_registros['C500'] = 0

        doc_pool = self.filial.pool.get('sped.documento')

        for nf in doc_pool.browse(self.cr, 1, self.bloco_c500_ids):
            if not self.ajusta_itens(nf):
                continue

            self.totais_registros['geral'] += 1
            self.totais_registros['C500'] += 1
            reg = '|C500'
            reg += '|' + nf.entrada_saida
            reg += '|' + nf.emissao
            reg += '|' + limpa_formatacao(nf.partner_id.cnpj_cpf)
            reg += '|' + nf.modelo
            reg += '|' + nf.situacao
            reg += '|' + (nf.serie or '')
            reg += '|' + (nf.subserie or '')

            #
            # Classe de consumo
            #
            if nf.modelo == '29':
                reg += '|' + nf.classe_consumo_agua
            elif nf.modelo == '28':
                reg += '|' + nf.classe_consumo_gas
            else:
                reg += '|' + nf.classe_consumo_energia

            reg += '|' + unicode(nf.numero)

            if nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            else:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

            #
            # Envia a data de entrada/saída somente se o mês e ano forem
            # iguais ao mês e ano da data de emissão
            #
            if not nf.data_entrada_saida_brasilia:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')
            elif nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            elif nf.data_emissao_brasilia[:7] == nf.data_entrada_saida_brasilia[:7]:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            else:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

            reg += '|' + formata_valor_sped(nf.vr_nf)

            reg += '|' + formata_valor_sped(nf.vr_desconto)
            reg += '|' + formata_valor_sped(nf.vr_produtos)
            reg += '|'
            reg += '|'
            reg += '|' + formata_valor_sped(nf.vr_outras)
            reg += '|' + formata_valor_sped(nf.bc_icms_proprio)
            reg += '|' + formata_valor_sped(D(nf.vr_icms_proprio) + D(nf.vr_icms_sn))
            reg += '|' + formata_valor_sped(nf.bc_icms_st)
            reg += '|' + formata_valor_sped(nf.vr_icms_st)
            reg += '|'
            reg += '|' + formata_valor_sped(nf.vr_pis_proprio)
            reg += '|' + formata_valor_sped(nf.vr_cofins_proprio)

            if nf.modelo == '06':
                reg += '|' + nf.tipo_ligacao_energia
                reg += '|' + nf.grupo_tensao_energia
            else:
                reg += '|'
                reg += '|'

            reg += '|\r\n'
            self._grava_registro(reg)

            #
            # Credita ou debita o ICMS próprio
            #
            if nf.situacao in [SITUACAO_FISCAL_REGULAR, SITUACAO_FISCAL_COMPLEMENTAR]:
                if nf.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                    self.total_icms_entradas += D(nf.vr_icms_proprio)
                else:
                    self.total_icms_saidas += D(nf.vr_icms_proprio)

            self.registro_resumo(nf, 'C590')

    #
    # Bloco D
    # Documentos Fiscais de serviços de transporte
    #
    def registro_D100(self):
        if len(self.bloco_d100_ids) == 0:
            return ''

        self.totais_registros['D100'] = 0

        doc_pool = self.filial.pool.get('sped.documento')

        for nf in doc_pool.browse(self.cr, 1, self.bloco_d100_ids):
            #if not self.ajusta_itens(nf):
                #continue

            self.totais_registros['geral'] += 1
            self.totais_registros['D100'] += 1
            reg = '|D100'
            reg += '|' + nf.entrada_saida
            reg += '|' + nf.emissao

            if nf.situacao in SITUACAO_FISCAL_SPED_CONSIDERA_CANCELADO:
                reg += '|'
            else:
                reg += '|' + limpa_formatacao(nf.partner_id.cnpj_cpf)

            reg += '|' + nf.modelo
            reg += '|' + nf.situacao
            reg += '|' + (nf.serie or '')
            reg += '|' + (nf.subserie or '')
            reg += '|' + unicode(nf.numero)

            if nf.situacao in SITUACAO_FISCAL_SPED_CONSIDERA_CANCELADO:
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|\r\n'
                self._grava_registro(reg)

            else:
                #if (nf.emissao == models.TIPO_EMISSAO_PROPRIA) and (nf.documentonfe != None):
                #    reg += '|' + nf.documentonfe.chave_nfe
                if nf.modelo == MODELO_FISCAL_CTE:
                    reg += '|' + nf.chave
                else:
                    reg += '|'

                if nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                else:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

                #
                # Envia a data de entrada/saída somente se o mês e ano forem
                # iguais ao mês e ano da data de emissão
                #
                if not nf.data_entrada_saida_brasilia:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')
                elif nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                elif nf.data_emissao_brasilia[:7] == nf.data_entrada_saida_brasilia[:7]:
                    reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
                else:
                    reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

                reg += '|'
                reg += '|'
                reg += '|' + formata_valor_sped(nf.vr_produtos)
                reg += '|' + formata_valor_sped(nf.vr_desconto)

                #
                # Converte da modalidade do frete da NF-e para a modalidade do frete
                # do SPED
                #
                if nf.modalidade_frete == MODALIDADE_FRETE_EMITENTE:
                    reg += '|1'
                elif nf.modalidade_frete == MODALIDADE_FRETE_DESTINATARIO:
                    reg += '|2'
                elif nf.modalidade_frete == MODALIDADE_FRETE_TERCEIROS:
                    reg += '|0'
                elif nf.modalidade_frete == MODALIDADE_FRETE_SEM_FRETE:
                    reg += '|9'

                reg += '|' + formata_valor_sped(nf.vr_produtos)
                reg += '|' + formata_valor_sped(nf.bc_icms_proprio)
                reg += '|' + formata_valor_sped(nf.vr_icms_proprio)
                reg += '|'
                reg += '|'
                reg += '|'
                reg += '|\r\n'
                self._grava_registro(reg)

                #
                # Credita ou debita o ICMS próprio
                #
                if nf.situacao in [SITUACAO_FISCAL_REGULAR, SITUACAO_FISCAL_COMPLEMENTAR]:
                    if nf.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                        self.total_icms_entradas += D(nf.vr_icms_proprio)
                    else:
                        self.total_icms_saidas += D(nf.vr_icms_proprio)

                self.registro_resumo(nf, 'D190')

    def registro_D500(self):
        if len(self.bloco_d500_ids) == 0:
            return ''

        self.totais_registros['D500'] = 0

        doc_pool = self.filial.pool.get('sped.documento')

        for nf in doc_pool.browse(self.cr, 1, self.bloco_d500_ids):
            if not self.ajusta_itens(nf):
                continue

            self.totais_registros['geral'] += 1
            self.totais_registros['D500'] += 1
            reg = '|D500'
            reg += '|' + nf.entrada_saida
            reg += '|' + nf.emissao
            reg += '|' + limpa_formatacao(nf.partner_id.cnpj_cpf)
            reg += '|' + nf.modelo
            reg += '|' + nf.situacao
            reg += '|' + (nf.serie or '')
            reg += '|' + (nf.subserie or '')
            reg += '|' + unicode(nf.numero)

            if nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            else:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

            #
            # Envia a data de entrada/saída somente se o mês e ano forem
            # iguais ao mês e ano da data de emissão
            #
            if not nf.data_entrada_saida_brasilia:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')
            elif nf.situacao in SITUACAO_FISCAL_EXTEMPORANEO:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            elif nf.data_emissao_brasilia[:7] == nf.data_entrada_saida_brasilia[:7]:
                reg += '|' + parse_datetime(nf.data_entrada_saida_brasilia).strftime('%d%m%Y')
            else:
                reg += '|' + parse_datetime(nf.data_emissao_brasilia).strftime('%d%m%Y')

            reg += '|' + formata_valor_sped(nf.vr_nf)
            reg += '|' + formata_valor_sped(nf.vr_desconto)
            reg += '|' + formata_valor_sped(nf.vr_produtos)
            reg += '|'
            reg += '|'
            reg += '|' + formata_valor_sped(nf.vr_outras)
            reg += '|' + formata_valor_sped(nf.bc_icms_proprio)
            reg += '|' + formata_valor_sped(D(nf.vr_icms_proprio) + D(nf.vr_icms_sn))
            reg += '|'
            reg += '|' + formata_valor_sped(nf.vr_pis_proprio)
            reg += '|' + formata_valor_sped(nf.vr_cofins_proprio)
            reg += '|'
            reg += '|' + nf.tipo_ligacao_energia
            reg += '|\r\n'
            self._grava_registro(reg)

            #
            # Credita ou debita o ICMS próprio
            #
            if nf.situacao in [SITUACAO_FISCAL_REGULAR, SITUACAO_FISCAL_COMPLEMENTAR]:
                if nf.entrada_saida == ENTRADA_SAIDA_ENTRADA:
                    self.total_icms_entradas += D(nf.vr_icms_proprio)
                else:
                    self.total_icms_saidas += D(nf.vr_icms_proprio)

            self.registro_resumo(nf, 'D590')

    #
    # Bloco E
    # Apuração do ICMS e do IPI
    #
    def registro_E100(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['E100'] = 1

        reg = '|E100'
        reg += '|' + self.data_inicial.strftime('%d%m%Y')
        reg += '|' + self.data_final.strftime('%d%m%Y')
        reg += '|\r\n'
        self._grava_registro(reg)
        #
        # Apuração do ICMS próprio
        #
        self.registro_E110()
        #
        # Apuração do ICMS ST
        #
        #self.registro_E200()

    def registro_E110(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['E110'] = 1

        reg = '|E110'
        reg += '|' + formata_valor_sped(self.total_icms_saidas)
        reg += '|0'
        reg += '|0'
        reg += '|0'
        reg += '|' + formata_valor_sped(self.total_icms_entradas)
        reg += '|0'
        reg += '|0'
        reg += '|0'
        reg += '|0'

        if self.total_icms_saidas > self.total_icms_entradas:
            self.credito_icms = self.total_icms_saidas - self.total_icms_entradas
            reg += '|' + formata_valor_sped(self.credito_icms)
            reg += '|0'
            reg += '|' + formata_valor_sped(self.credito_icms)
            reg += '|0'
        else:
            self.debito_icms = self.total_icms_entradas - self.total_icms_saidas
            reg += '|0'
            reg += '|0'
            reg += '|0'
            reg += '|' + formata_valor_sped(self.debito_icms)

        reg += '|0'
        reg += '|\r\n'
        self._grava_registro(reg)

        # Se há ICMS a recolher, gerar o registro E116
        self.registro_E116()

    def registro_E116(self):
        if self.debito_icms <= 0:
            return

        self.totais_registros['geral'] += 1
        self.totais_registros['E116'] = 1

        reg = '|E116'
        reg += '|000'
        reg += '|' + formata_valor_sped(self.debito_icms)
        reg += '|' + self.data_final.strftime('%d%m%Y')
        reg += '|CONTADOR, PREENCHA O CÓDIGO CORRETO'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|' + self.data_inicial.strftime('%m%Y')
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_E200(self):
        estados_com_st = self.doc_icms.filter(vr_icms_st__gt=0).values('participante__municipio__estado').annotate(models.Count('id')).order_by()
        print(estados_com_st)

        for item in estados_com_st:
            estado = item['participante__municipio__estado']
            self.totais_registros['geral'] += 1

            if not 'E200' in self.totais_registros.keys():
                self.totais_registros['E200'] = 1
            else:
                self.totais_registros['E200'] += 1

            reg = '|E200'
            reg += '|' + estado
            reg += '|' + self.data_inicial.strftime('%d%m%Y')
            reg += '|' + self.data_final.strftime('%d%m%Y')
            reg += '|\r\n'
            self._grava_registro(reg)
            self.registro_E210(estado)

    def registro_E210(self, estado):
        self.totais_registros['geral'] += 1

        if not 'E210' in self.totais_registros.keys():
            self.totais_registros['E210'] = 1
        else:
            self.totais_registros['E210'] += 1

        documentos = self.doc_icms.filter(participante__municipio__estado=estado, situacao__in=models.SITUACAO_FISCAL_SPED_CONSIDERA_ATIVO)

        icms_devolucao = documentos.filter(notafiscalitem__cfop__codigo__in=CFOP_DEVOLUCAO).values('entrada_saida').annotate(total_icms_st=Sum('vr_icms_st')).order_by()
        icms_ressarcimento = documentos.filter(notafiscalitem__cfop__codigo__in=CFOP_RESSARCIMENTO).values('entrada_saida').annotate(total_icms_st=Sum('vr_icms_st')).order_by()
        icms_saidas = documentos.filter(entrada_saida=models.ENTRADA_SAIDA_SAIDA).values('entrada_saida').annotate(total_icms_st=Sum('vr_icms_st')).order_by()
        icms_entradas = documentos.filter(entrada_saida=models.ENTRADA_SAIDA_ENTRADA).exclude(
            notafiscalitem__cfop__codigo__in=CFOP_DEVOLUCAO+CFOP_RESSARCIMENTO
        ).values('entrada_saida').annotate(total_icms_st=Sum('vr_icms_st')).order_by()

        print(icms_devolucao)
        print(icms_ressarcimento)
        print(icms_saidas)

        reg = '|E210'
        reg += '|1'

        # Saldo credor do período anterior
        reg += '|0'

        # ICMS vindo da devolução de mercadorias
        total_icms_devolucao = 0
        if icms_devolucao:
            for dev in icms_devolucao:
                total_icms_devolucao += dev['total_icms_st']

            reg += '|' + formata_valor_sped(total_icms_devolucao)

        else:
            reg += '|0'

        # ICMS vindo de ressarcimento de ICMS
        total_icms_ressarcimento = 0
        if icms_ressarcimento:
            for res in icms_ressarcimento:
                total_icms_ressarcimento += res['total_icms_st']

            reg += '|' + formata_valor_sped(total_icms_ressarcimento)
        else:
            reg += '|0'

        # Outras entradas de ICMS ST
        total_icms_entradas = 0
        if icms_entradas:
            for ent in icms_entradas:
                total_icms_entradas += ent['total_icms_st']

            reg += '|' + formata_valor_sped(total_icms_entradas)
        else:
            reg += '|0'

        # Ajustes a crédito
        reg += '|0'

        # Total do ST retido
        total_icms_saidas = 0
        if icms_saidas:
            for sai in icms_saidas:
                total_icms_saidas += sai['total_icms_st']

            reg += '|' + formata_valor_sped(total_icms_saidas)
        else:
            reg += '|0'

        # Total de outros débitos
        reg += '|0'

        # Ajustes a débito
        reg += '|0'

        # Saldo devedor antes das deduções
        if ((total_icms_devolucao + total_icms_ressarcimento + total_icms_entradas) > total_icms_saidas):
            icms_apurado = 0
            icms_creditado = (total_icms_devolucao + total_icms_ressarcimento + total_icms_entradas) - total_icms_saidas
            reg += '|0'
        else:
            icms_apurado = total_icms_saidas - (total_icms_devolucao + total_icms_ressarcimento + total_icms_entradas)
            icms_creditado = 0
            reg += '|' + formata_valor_sped(icms_apurado)

        # Total das deduções
        reg += '|0'

        # ICMS ST a recolher
        reg += '|' + formata_valor_sped(icms_apurado)

        # ICMS ST a creditar
        reg += '|' + formata_valor_sped(icms_creditado)

        # Valores recolhidos ou a recolher, extra-apuração
        reg += '|0'
        reg += '|\r\n'
        self._grava_registro(reg)
        self.registro_E250(estado, icms_apurado)

    def registro_E250(self, estado, icms_apurado):
        if icms_apurado == 0:
            return ''

        self.totais_registros['geral'] += 1

        if not 'E250' in self.totais_registros.keys():
            self.totais_registros['E250'] = 1
        else:
            self.totais_registros['E250'] += 1

        reg = '|E250'

        if estado == self.filial.municipio.estado:
            reg += '|002'
        else:
            reg += '|999'

        reg += '|' + formata_valor_sped(icms_apurado)
        reg += '|' + self.data_final.strftime('%d%m%Y')
        reg += '|CONTADOR, PREENCHA O CÓDIGO CORRETO'

        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|'
        reg += '|' + self.data_final.strftime('%m%Y')
        reg += '|\r\n'
        self._grava_registro(reg)

    #
    # Apuração do IPI
    #
    def registro_E500(self):
        #
        # Se nenhuma nota tem valor do IPI, não gerar registros
        #
        if self.doc_ipi.count() == 0:
            return

        self.totais_registros['geral'] += 1
        self.totais_registros['E500'] = 1

        reg = '|E500'
        reg += '|0' # Apuração mensal
        reg += '|' + self.data_inicial.strftime('%d%m%Y')
        reg += '|' + self.data_final.strftime('%d%m%Y')
        reg += '|\r\n'
        self._grava_registro(reg)
        self.registro_E510()
        self.registro_E520()

    def registro_E510(self):
        if not 'E510' in self.totais_registros.keys():
            self.totais_registros['E510'] = 0

        #
        # Atenção!!!
        # No annotate lembrar sempre de colocar o order_by() vazio!!!
        # http://docs.djangoprojenf.com/en/1.3/topics/db/aggregation/#interaction-with-default-ordering-or-order-by
        #
        resumos_analiticos_qs = NotaFiscalItem.objects.filter(notafiscal__in=self.doc_ipi_rezumo.only('id')).exclude(cst_ipi='XX').exclude(cst_ipi=None).exclude(cst_ipi='').values('cfop__codigo', 'cst_ipi')

        resumos_analiticos = resumos_analiticos_qs.annotate(
            vr_nf_agrupado=Sum('vr_nf'),
            bc_ipi_agrupado=Sum('bc_ipi'),
            vr_ipi_agrupado=Sum('vr_ipi')
        ).order_by()

        for resumo in resumos_analiticos:
            self.totais_registros['geral'] += 1
            self.totais_registros['E510'] += 1
            reg = '|E510'
            reg += '|' + resumo['cfop__codigo']
            reg += '|' + resumo['cst_ipi']
            reg += '|' + formata_valor_sped(resumo['vr_nf_agrupado'])
            reg += '|' + formata_valor_sped(resumo['bc_ipi_agrupado'])
            reg += '|' + formata_valor_sped(resumo['vr_ipi_agrupado'])
            reg += '|\r\n'
            self._grava_registro(reg)

    def registro_E520(self):
        self.totais_registros['geral'] += 1
        self.totais_registros['E520'] = 1

        nf_entradas = self.doc_ipi.filter(entrada_saida=models.ENTRADA_SAIDA_ENTRADA)
        nf_entradas = nf_entradas.aggregate(soma_vr_ipi=Sum('vr_ipi'))

        nf_saidas = self.doc_ipi.filter(entrada_saida=models.ENTRADA_SAIDA_SAIDA)
        nf_saidas = nf_saidas.aggregate(soma_vr_ipi=Sum('vr_ipi'))

        if nf_entradas and nf_entradas['soma_vr_ipi']:
            total_vr_ipi_entrada = nf_entradas['soma_vr_ipi']
        else:
            total_vr_ipi_entrada = 0

        if nf_saidas and nf_saidas['soma_vr_ipi']:
            total_vr_ipi_saida = nf_saidas['soma_vr_ipi']
        else:
            total_vr_ipi_saida = 0

        reg = '|E520'
        reg += '|0'
        reg += '|' + formata_valor_sped(total_vr_ipi_saida)
        reg += '|' + formata_valor_sped(total_vr_ipi_entrada)
        reg += '|0'
        reg += '|0'

        if total_vr_ipi_saida > total_vr_ipi_entrada:
            reg += '|0'
            reg += '|' + formata_valor_sped(total_vr_ipi_saida - total_vr_ipi_entrada)
        else:
            reg += '|' + formata_valor_sped(total_vr_ipi_entrada - total_vr_ipi_saida)
            reg += '|0'

        reg += '|\r\n'
        self._grava_registro(reg)

    #
    # Bloco H - inventário
    #
    def registro_H005(self):
        if not self.movimentos_blocos['H']:
            return

        self.totais_registros['geral'] += 1
        self.totais_registros['H005'] = 1

        soma_valores = D(0)
        for produto_id in self.itens_inventario:
            soma_valores += self.itens_inventario[produto_id][2]

        reg = '|H005'
        reg += '|' + self.data_inventario.strftime('3112%Y')
        reg += '|' + formata_valor_sped(soma_valores or 0)
        reg += '|\r\n'
        self._grava_registro(reg)

        if len(self.itens_inventario):
            self.registro_H010()

    def registro_H010(self):
        if len(self.itens_inventario) == 0:
            return ''

        if not 'H010' in self.totais_registros.keys():
            self.totais_registros['H010'] = 0

        product_pool = self.filial.pool.get('product.product')

        for produto_id in self.itens_inventario:
            produto = product_pool.browse(self.cr, 1, produto_id)
            self.totais_registros['geral'] += 1
            self.totais_registros['H010'] += 1

            quantidade = D(self.itens_inventario[produto_id][0] or 1)
            custo_medio = self.itens_inventario[produto_id][1]
            valor = self.itens_inventario[produto_id][2]

            reg = '|H010'
            reg += '|' + (produto.default_code or '')

            if self.questor:
                reg += '|' + produto.uom_id.name or ''
            else:
                reg += '|' + str(produto.uom_id.id)

            reg += '|' + formata_valor_sped(quantidade, decimais=3)
            reg += '|' + formata_valor_sped(custo_medio, decimais=6)
            reg += '|' + formata_valor_sped(valor)
            #reg += '|' + item.propriedade

            #if item.participante == None:
                #reg += '|'
            #else:
                #reg += '|' + item.participante.cnpj_cpf

            #reg += '|'
            #reg += '|' + item.conta_contabil.strip()
            reg += '|0'
            reg += '|' # cnpj
            reg += '|' # descrição complementar
            reg += '|' # conta contábil
            reg += '|' # valor do item para o IR
            reg += '|\r\n'
            self._grava_registro(reg)

    #
    # Bloco 9
    # Controle e encerramento do arquivo digital
    #
    def registro_9900(self):
        #
        # Temos que considerar o total dos registros 9990 e 9999 também
        #
        self.totais_registros['9900'] = 0
        self.totais_registros['9990'] = 1
        self.totais_registros['9999'] = 1

        tipos_registro = self.totais_registros.keys()
        #tipos_registro.sort()

        for tipo_registro in tipos_registro:
            if (tipo_registro != 'geral') and (tipo_registro != '9900'):
                self.totais_registros['geral'] += 1
                self.totais_registros['9900'] += 1
                reg = '|9900'
                reg += '|' + tipo_registro
                reg += '|' + unicode(self.totais_registros[tipo_registro])
                reg += '|\r\n'
                self._grava_registro(reg)

        self.totais_registros['geral'] += 1
        self.totais_registros['9900'] += 1
        reg = '|9900'
        reg += '|9900'
        reg += '|' + unicode(self.totais_registros['9900'])
        reg += '|\r\n'
        self._grava_registro(reg)

    def registro_9999(self):
        self.totais_registros['geral'] += 1
        reg = '|9999'
        reg += '|' + unicode(self.totais_registros['geral'])
        reg += '|\r\n'
        self._grava_registro(reg)

    def ajusta_itens(self, nf):
        if nf.emissao == TIPO_EMISSAO_PROPRIA:
            return True

        total_bc_icms_proprio = D(0)
        total_vr_icms_proprio = D(0)
        #total_bc_icms_st = D(0)
        #total_vr_icms_st = D(0)
        #total_vr_ipi = D(0)

        retorno = True
        for item in nf.documentoitem_ids:
            if item.credita_icms_proprio:
                total_bc_icms_proprio += D(item.bc_icms_proprio)
                total_vr_icms_proprio += D(item.vr_icms_proprio)

            if (not item.produto_id) or (not item.cfop_id):
                retorno = False
                continue

            if item.vr_nf and item.vr_produtos:
                retorno = False
                continue

            dados = calcula_item(item, self.cr, 1, item)
            item.write(dados)

        if (not nf.vr_nf) or (not nf.vr_produtos):
            nf.write({'recalculo': int(time())})

        nf.bc_icms_proprio = total_bc_icms_proprio
        nf.vr_icms_proprio = total_vr_icms_proprio

        return retorno

    def monta_resumo(self, nf):
        nf._resumo_sped = {}

        if True:
        #try:
            for item in nf.documentoitem_ids:
                if not item.org_icms:
                    item.org_icms = '0'
                if not item.cst_icms:
                    item.cst_icms = '41'
                #
                # Monta o _resumo_sped do C190
                #
                if item.documento_id.regime_tributario == REGIME_TRIBUTARIO_SIMPLES:
                    chave_resumo = item.cst_icms_sn
                else:
                    chave_resumo = item.org_icms + item.cst_icms

                if item.cfop_id:
                    chave_resumo += '_' + item.cfop_id.codigo + '_'
                else:
                    chave_resumo += '_' + '' + '_'

                if item.emissao == '0' or (item.documento_id.entrada_saida == '0' and item.credita_icms_proprio):
                    chave_resumo += formata_valor_sped(item.al_icms_proprio)
                else:
                    chave_resumo += formata_valor_sped(0)

                if chave_resumo not in nf._resumo_sped:
                    nf._resumo_sped[chave_resumo] = {
                        'vr_produtos': D(0),
                        'bc_icms_proprio': D(0),
                        'vr_icms_proprio': D(0),
                        'bc_icms_st': D(0),
                        'vr_icms_st': D(0),
                        'vr_ipi': D(0),
                        'vr_nf': D(0),
                    }

                nf._resumo_sped[chave_resumo]['vr_produtos'] += D(item.vr_produtos)

                if item.emissao == '0' or (item.documento_id.entrada_saida == '0' and item.credita_icms_proprio):
                    nf._resumo_sped[chave_resumo]['bc_icms_proprio'] += D(item.bc_icms_proprio)
                    nf._resumo_sped[chave_resumo]['vr_icms_proprio'] += D(item.vr_icms_proprio)

                if item.emissao == '0':
                    nf._resumo_sped[chave_resumo]['bc_icms_st'] += D(item.bc_icms_st)
                    nf._resumo_sped[chave_resumo]['vr_icms_st'] += D(item.vr_icms_st)

                nf._resumo_sped[chave_resumo]['vr_ipi'] += D(item.vr_ipi)
                nf._resumo_sped[chave_resumo]['vr_nf'] += D(item.vr_nf)

        #except:
            #raise Exception(u'Erro!', u'Item com problemas na NF modelo %s nº %s, do dia %s' % (nf.modelo, nf.numero, parse_datetime(nf.data_emissao_brasilia).strftime('%d/%m/%Y')))

    def registro_resumo(self, nf, registro):
        self.monta_resumo(nf)

        if (not hasattr(nf, '_resumo_sped')) or (not len(nf._resumo_sped)):
            return ''

        if not registro in self.totais_registros.keys():
            self.totais_registros[registro] = 0

        for chave_resumo in nf._resumo_sped:
            self.totais_registros['geral'] += 1
            self.totais_registros[registro] += 1
            reg = '|' + registro

            cst_icms, cfop, al_icms_proprio = chave_resumo.split('_')
            vr_nf = nf._resumo_sped[chave_resumo]['vr_nf']
            vr_produtos = nf._resumo_sped[chave_resumo]['vr_produtos']
            bc_icms_proprio = nf._resumo_sped[chave_resumo]['bc_icms_proprio']
            vr_icms_proprio = nf._resumo_sped[chave_resumo]['vr_icms_proprio']
            bc_icms_st = nf._resumo_sped[chave_resumo]['bc_icms_st']
            vr_icms_st = nf._resumo_sped[chave_resumo]['vr_icms_st']

            if registro == 'C190':
                vr_ipi = nf._resumo_sped[chave_resumo]['vr_ipi']

            reg += '|' + cst_icms
            reg += '|' + cfop
            reg += '|' + al_icms_proprio
            reg += '|' + formata_valor_sped(vr_nf)
            reg += '|' + formata_valor_sped(bc_icms_proprio)
            reg += '|' + formata_valor_sped(vr_icms_proprio)

            if registro not in ['D190']:
                reg += '|' + formata_valor_sped(bc_icms_st)
                reg += '|' + formata_valor_sped(vr_icms_st)

            if (vr_produtos >= bc_icms_proprio) or (cst_icms[1:3] in ('20', '70')):
                if vr_produtos >= bc_icms_proprio:
                    reg += '|' + formata_valor_sped(vr_produtos - bc_icms_proprio)
                else:
                    reg += '|' + formata_valor_sped(bc_icms_proprio - vr_produtos)
            else:
                reg += '|0,00'

            if registro in ['C190']:
                reg += '|' + formata_valor_sped(vr_ipi)

            reg += '|'
            reg += '|\r\n'
            self._grava_registro(reg)

    def prepara_ids(self):
        #
        # Todos os tipos de documento
        #
        if self.questor:
            self.sql_doc = """
            select
                d.id
            from
                sped_documento d
                join res_company c on c.id = d.company_id
                join res_partner p on p.id = c.partner_id
            where
                p.cnpj_cpf = '{cnpj}'
                and d.modelo != 'TF'
                and (
                      (d.data_entrada_saida_brasilia is null and d.data_emissao_brasilia between '{data_inicial}' and '{data_final}')
                    or d.data_entrada_saida_brasilia between '{data_inicial}' and '{data_final}'
                )
                --and cast(d.create_date at time zone 'America/Sao_Paulo' as date) between '{data_inicial}' and '{data_final}'
                and d.numero > 0
                and not exists(select di.documento_id from sped_documentoitem di where di.documento_id = d.id and (di.produto_id is null or di.cfop_id is null))
            """
        else:
            self.sql_doc = """
            select
                d.id
            from
                sped_documento d
                join res_company c on c.id = d.company_id
                join res_partner p on p.id = c.partner_id
            where
                p.cnpj_cpf = '{cnpj}'
                and d.modelo != 'TF'
                and (
                      (d.data_entrada_saida_brasilia is null and d.data_emissao_brasilia between '{data_inicial}' and '{data_final}')
                    or d.data_entrada_saida_brasilia between '{data_inicial}' and '{data_final}'
                )
                and d.numero > 0
                and not exists(select di.documento_id from sped_documentoitem di where di.documento_id = d.id and (di.produto_id is null or di.cfop_id is null))
            """

        if self.questor:
            self.sql_c100 = self.sql_doc + """
                and (
                        d.emissao = '0'
                    or d.situacao in ('00', '01')
                )
            order by
                d.modelo,
                d.data_emissao_brasilia,
                d.serie,
                d.numero;
            """
        else:
            self.sql_c100 = self.sql_doc + """
                and d.modelo in {MODELO_FISCAL_SPED_NF}
                and (
                        d.emissao = '0'
                    or d.situacao in ('00', '01')
                )
            order by
                d.modelo,
                d.data_emissao_brasilia,
                d.serie,
                d.numero;
            """

        self.sql_c500 = self.sql_doc + """
            and d.modelo in {MODELO_FISCAL_SPED_ENERGIA}
            and d.emissao = '1' and d.situacao in ('00', '01')
        order by
            d.modelo,
            d.data_emissao_brasilia,
            d.serie,
            d.numero;
        """

        self.sql_d100 = self.sql_doc + """
            and d.emissao = '1'
            and d.modelo in {MODELO_FISCAL_SPED_TRANSPORTE}
            and d.situacao in ('00', '01')
        order by
            d.modelo,
            d.data_emissao_brasilia,
            d.serie,
            d.numero;
        """

        self.sql_d500 = self.sql_doc + """
            and d.emissao = '1'
            and d.modelo in {MODELO_FISCAL_SPED_TELEFONE}
            and d.situacao in ('00', '01')
        order by
            d.modelo,
            d.data_emissao_brasilia,
            d.serie,
            d.numero;
        """

        self.bloco_c100_ids = self._busca_ids(self.sql_c100)
        if self.questor:
            self.bloco_c500_ids = []
        else:
            self.bloco_c500_ids = self._busca_ids(self.sql_c500)

        self.bloco_c_ids = self.bloco_c100_ids + self.bloco_c500_ids

        #if self.questor:
            #self.bloco_d100_ids = []
            #self.bloco_d500_ids = []
        #else:
        self.bloco_d100_ids = self._busca_ids(self.sql_d100)
        self.bloco_d500_ids = self._busca_ids(self.sql_d500)

        self.bloco_d_ids = self.bloco_d100_ids + self.bloco_d500_ids


        #
        # Inventário é obrigatório no mês de fevereiro
        #
        self.produtos_inventario = []
        self.itens_inventario = OrderedDict()
        if self.data_inicial.month == 2 and len(self.locais_estoque) > 0:
            self.sql_inventario = """
                select
                    es.company_id,
                    es.location_id,
                    pp.default_code,
                    es.product_id,
                    sum(
                        case
                            when es.tipo = 'S' then es.quantidade * -1
                            else es.quantidade
                        end
                    ) as quantidade,
                    coalesce(
                        (select
                            cm.vr_total / cm.quantidade
                        from
                            custo_medio(es.company_id, es.location_id, es.product_id) cm
                        where
                            cm.data <= '{data_inventario}'
                            and cm.vr_total > 0
                        order by
                            cm.data desc,
                            cm.entrada_saida desc,
                            cm.move_id desc
                        limit 1
                        ), 0) as custo_medio

                from
                    estoque_entrada_saida es
                    join stock_location sl on sl.id = es.location_id
                    join product_product pp on pp.id = es.product_id
                    join res_company c on c.id = es.company_id

                where
                    es.location_id in {location_ids}
                    and es.data <= '{data_inventario}'
                    and sl.usage = 'internal'
                    and c.cnpj_cpf = '{cnpj}'

                group by
                    es.company_id,
                    es.location_id,
                    pp.default_code,
                    es.product_id

                having
                    sum(
                        case
                            when es.tipo = 'S' then es.quantidade * -1
                            else es.quantidade
                        end
                    ) > 0

                order by
                    pp.default_code;
            """

            self.data_inventario = self.data_inicial + relativedelta(day=31, month=12, years=-1)
            dados_inventario = self._busca_ids(self.sql_inventario, {'data_inventario': self.data_inventario.strftime('%Y-12-31'), 'location_ids': tuple(self.locais_estoque)}, varios_campos=True)
            if len(dados_inventario) > 0:
                self.movimentos_blocos['H'] = True
                product_pool = self.filial.pool.get('product.product')

                for company_id, location_id, default_code, product_id, quantidade, custo_medio in dados_inventario:
                    if default_code == '00136':
                        print('company_id', company_id)
                        print('location_id', location_id)
                    if not product_id in self.itens_inventario:
                        self.itens_inventario[product_id] = [D(0), D(0), D(0)]

                    quantidade = D(quantidade or 1)
                    quantidade = quantidade.quantize(D('0.01'))
                    custo_medio = D(custo_medio)
                    custo_medio = custo_medio.quantize(D('0.01'))

                    self.itens_inventario[product_id][0] += quantidade
                    if custo_medio > self.itens_inventario[product_id][1]:
                        self.itens_inventario[product_id][1] = custo_medio

                codigos_ordem = self.itens_inventario.keys()
                codigos_ordem.sort()
                for produto_id in codigos_ordem:
                    linha = self.itens_inventario[produto_id]

                    if linha[1] == 0:
                        produto_obj = product_pool.browse(self.cr, 1, produto_id)
                        linha[1] = D(produto_obj.standard_price or 1)

                    linha[1] = D(linha[1]).quantize(D('0.01'))
                    linha[2] = D(linha[0] * linha[1]).quantize(D('0.01'))

                self.produtos_inventario = self.itens_inventario.keys()

        #
        # Participantes de todos os documentos envolvendo ICMS, desde que ativos, ou sejam terceiros no inventário
        #
        self.sql_participantes = """
        select
            p.id
        from
            res_partner p
            join sped_documento d on d.partner_id = p.id
        where
            d.id in {DOC_IDS}
        order by
            p.cnpj_cpf;
        """

        #if (self.inventario.count() == 0) or (self.inventario[0].inventarioitem_set.count() == 0):
        #self.participantes = Participante.objects.filter(fis_notafiscal_participante__in=doc_icms_ativos_participantes).distinct()
        #else:
            #self.participantes = Participante.objects.filter(
                #models.Q(fis_notafiscal_participante__in=doc_icms_ativos_participantes) | models.Q(inventarioitem__in=self.inventario[0].inventarioitem_set.all())).distinct()

        self.participante_ids = self._busca_ids(self.sql_participantes, {'DOC_IDS': tuple(self.bloco_c_ids + self.bloco_d_ids)})

        #notasterceiros = self.notasfiscais.filter(emissao=models.TIPO_EMISSAO_TERCEIROS).only('id')
        #notasterceiros = self.notasfiscais.all().only('id')
        #itensterceiros = NotaFiscalItem.objects.filter(notafiscal__in=notasterceiros).only('produtoservico__id')

        #if (self.inventario.count() == 0) or (self.inventario[0].inventarioitem_set.count() == 0):
            #self.produtos = ProdutoServico.objects.filter(notafiscalitem__in=itensterceiros).distinct()
        #else:
            #self.produtos = ProdutoServico.objects.filter(
                #models.Q(notafiscalitem__in=itensterceiros) | models.Q(inventarioitem__in=self.inventario[0].inventarioitem_set.all())).distinct()

        #
        # Produtos, unidades e naturezas de operação, somente de notas de terceiros
        #
        if self.questor:
            self.sql_produtos = """
            select
                p.id
            from
                product_product p
                join sped_documentoitem di on di.produto_id = p.id
                join sped_documento d on di.documento_id = d.id
            where
                -- d.emissao = '1' and
                d.id in {DOC_IDS}
            order by
                p.id;
            """

        else:
            self.sql_produtos = """
            select
                p.id
            from
                product_product p
                join sped_documentoitem di on di.produto_id = p.id
                join sped_documento d on di.documento_id = d.id
            where
                d.emissao = '1' and
                d.id in {DOC_IDS}
            order by
                p.id;
            """
        self.produto_ids = self._busca_ids(self.sql_produtos, {'DOC_IDS': tuple(self.bloco_c_ids + self.bloco_d_ids)})
        self.produto_ids += self.produtos_inventario

        #self.unidades = Unidade.objects.filter(cad_produtoservico_unidade__in=self.produtos).distinct()
        self.sql_unidades = """
        select
            u.id
        from
            product_uom u
            join product_template t on t.uom_id = u.id
            join product_product p on p.product_tmpl_id = t.id
        where
            p.id in {PRODUTO_IDS}
        order by
            u.name;
        """
        self.unidade_ids = self._busca_ids(self.sql_unidades, {'PRODUTO_IDS': tuple(self.produto_ids)})

        #self.naturezas = NaturezaOperacao.objects.filter(notafiscal__in=notasterceiros).distinct()
        self.sql_naturezas = """
        select
            n.id
        from
            sped_naturezaoperacao n
            join sped_documento d on d.naturezaoperacao_id = n.id
        where
            d.emissao = '1'
            and d.id in {DOC_IDS}
        order by
            n.codigo;
        """
        self.natureza_ids = self._busca_ids(self.sql_naturezas, {'DOC_IDS': tuple(self.bloco_c_ids + self.bloco_d_ids)})

        if len(self.bloco_c_ids):
            self.movimentos_blocos['C'] = True
            self.movimentos_blocos['E'] = True

        print(self.bloco_d_ids, 'bloco d')
        if len(self.bloco_d_ids):
            self.movimentos_blocos['D'] = True
            self.movimentos_blocos['E'] = True
