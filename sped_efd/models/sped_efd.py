# -*- coding: utf-8 -*-
import base64
import datetime

from sped.efd.icms_ipi import arquivos, registros
from odoo import fields, models, api

from l10n_br_base.constante_tributaria import MODELO_FISCAL_NFE, MODELO_FISCAL_NFCE


class SpedEFD(models.Model):
    _name = 'sped.efd'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        select=True,
    )
    fci_file_sent = fields.Many2one(
        comodel_name='ir.attachment',
        string='Arquivo',
        ondelete='restrict',
        copy=False,
    )
    dt_ini = fields.Datetime(
        string='Data inicial',
        index=True,
        default=fields.Datetime.now,
        required=True,
    )
    dt_fim = fields.Datetime(
        string='Data final',
        index=True,
        required=True,
    )

    @property
    def versao(self):
        if fields.Datetime.from_string(self.dt_ini) >= datetime.datetime(2016, 1, 1):
            return '011'

        return '009'

    def transforma_data(self, data):  # aaaammdd
        data = self.limpa_formatacao(data)
        return data[6:] + data[4:6] + data[:4]

    def limpa_formatacao(self, data):
        if data:
            replace = ['-', ' ', '(', ')', '/', '.', ':']
            for i in replace:
                data = data.replace(i, '')

        return data

    def formata_cod_municipio(self, data):
        return data[:7]

    def query_registro0000(self):
        query = """
            select DISTINCT
                p.id, m.id 
            from 
                sped_documento as d 
                join sped_empresa as e on d.empresa_id=e.id
                join sped_participante as p on e.participante_id=p.id 
                join sped_municipio as m on m.id=p.municipio_id
                join res_company as c on e.company_id=c.id
            where
                e.company_id='%s'
        """ % (self.company_id.id)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        resposta_participante = self.env['sped.participante'].browse(query_resposta[0][0])
        resposta_municipio = self.env['sped.municipio'].browse(query_resposta[0][1])
        registro_0000 = registros.Registro0000()
        registro_0000.COD_VER = str(self.versao)
        registro_0000.COD_FIN = '0'  # finalidade
        registro_0000.DT_INI = self.transforma_data(self.dt_ini[:10])  # data_inicio
        registro_0000.DT_FIN = self.transforma_data(self.dt_fim[:10])  # data_final
        registro_0000.NOME = resposta_participante.nome  # filial.razao_social (?)
        cpnj_cpf = self.limpa_formatacao(resposta_participante.cnpj_cpf)
        if len(cpnj_cpf) == 11:
            registro_0000.CPF = cpnj_cpf
        else:
            registro_0000.CNPJ = cpnj_cpf
        registro_0000.UF = resposta_municipio.estado  # filial.estado
        registro_0000.IE = self.limpa_formatacao(resposta_participante.ie)
        registro_0000.COD_MUN = self.formata_cod_municipio(
            resposta_municipio.codigo_ibge)  # filial.municipio_id.codigo_ibge[:7]
        registro_0000.IM = resposta_participante.im  # filial.im
        registro_0000.SUFRAMA = self.limpa_formatacao(resposta_participante.suframa)  # filial.suframa
        registro_0000.IND_PERFIL = 'A'  # perfil
        registro_0000.IND_ATIV = '1'  # tipo_atividade
        return registro_0000

    def query_registro0100(self):
        query = """
                    select 
                        p.id, m.id
                    from 
                        sped_empresa as e
                        join sped_participante as p on e.participante_id=p.id
                        join sped_municipio as m on p.municipio_id=m.id
                    where 
                        e.company_id='%s'
        """ % (self.company_id.id)
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        resposta = self.env['sped.participante'].browse(query_resposta[0][0])
        resposta_municipio = self.env['sped.municipio'].browse(query_resposta[0][1])
        registro_0100 = registros.Registro0100()
        registro_0100.NOME = resposta.nome
        cpnj_cpf = self.limpa_formatacao('11166072630')
        if len(cpnj_cpf) == 11:
            registro_0100.CPF = cpnj_cpf
        else:
            registro_0100.CNPJ = cpnj_cpf
        registro_0100.CRC = '111111111111111' # TODO: resposta.crc
        registro_0100.CEP = self.limpa_formatacao(resposta.cep)
        registro_0100.END = resposta.endereco
        registro_0100.NUM = resposta.numero
        registro_0100.COMPL = resposta.complemento
        registro_0100.BAIRRO = resposta.bairro
        registro_0100.FONE = self.limpa_formatacao(resposta.fone)
        registro_0100.EMAIL = '123456@gmail.com' # TODO: resposta.email
        registro_0100.COD_MUN = self.formata_cod_municipio(resposta_municipio.codigo_ibge)

        return registro_0100

    def query_registro0005(self):
        query = """
             select
                 p.id
             from
                 sped_empresa as e
                 join sped_participante as p on e.participante_id=p.id
             where
                 e.company_id='%s'
        """ % self.company_id.id
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []

        for id in query_resposta:
            resposta = self.env['sped.participante'].browse(id[0])
            registro_0005 = registros.Registro0005()
            registro_0005.FANTASIA = resposta.fantasia
            registro_0005.CEP = self.limpa_formatacao(resposta.cep)
            registro_0005.END = resposta.endereco
            registro_0005.NUM = resposta.numero
            registro_0005.COMPL = resposta.complemento
            registro_0005.BAIRRO = resposta.bairro
            registro_0005.FONE = self.limpa_formatacao(resposta.fone)
            registro_0005.EMAIL = resposta.email
            lista.append(registro_0005)

        return registro_0005

    def query_registro0150(self):
        # TODO: lista de participantes
        query = """
                    select distinct 
                        p.id, m.id
                    from
                        sped_natureza_operacao n 
                        join sped_documento d on d.natureza_operacao_id = n.id
                        join sped_documento_item as i on d.id=i.documento_id
                        join sped_empresa c on c.id = d.empresa_id
                        join sped_participante p on p.id = c.participante_id
                        join sped_municipio as m on m.id=p.municipio_id
                    where
                        d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
                """ % (self.dt_ini[:10], self.dt_fim[:10])

        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for id in query_resposta:
            resposta_participante = self.env['sped.participante'].browse(id[0])
            resposta_municipio = self.env['sped.municipio'].browse(id[1])
            registro_0150 = registros.Registro0150()
            registro_0150.COD_PART = str(resposta_participante.id)
            registro_0150.NOME = resposta_participante.nome
            registro_0150.COD_PAIS = resposta_municipio.pais_id.codigo_bacen
            cpnj_cpf = self.limpa_formatacao(resposta_participante.cnpj_cpf)
            if len(cpnj_cpf) == 11:
                registro_0150.CPF = cpnj_cpf
            else:
                registro_0150.CNPJ = cpnj_cpf
            registro_0150.IE = self.limpa_formatacao(resposta_participante.ie)
            registro_0150.COD_MUN = self.formata_cod_municipio(resposta_municipio.codigo_ibge)
            registro_0150.SUFRAMA = self.limpa_formatacao(resposta_participante.suframa)
            registro_0150.END = resposta_participante.endereco.rstrip()
            registro_0150.NUM = resposta_participante.numero
            registro_0150.COMPL = resposta_participante.complemento
            registro_0150.BAIRRO = resposta_participante.bairro
            lista.append(registro_0150)

        return lista

    def query_registro0190(self):
        query = """
                    select distinct 
                       u.codigo_unico, u.nome_unico 
                    from
                        sped_documento as d
                        join sped_documento_item as di on d.id=di.documento_id 
                        join sped_produto as p on di.produto_id=p.id
                        join sped_unidade as u on p.unidade_id=u.id
                    where
                        d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
                """ % (self.dt_ini[:10], self.dt_fim[:10])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for resposta in query_resposta:
            registro_0190 = registros.Registro0190()
            registro_0190.UNID = resposta[0]
            registro_0190.DESCR = resposta[1]
            lista.append(registro_0190)
        return lista

    def query_registro0400(self):
        query = """
                    select distinct 
                       no.codigo_unico, no.nome 
                    from
                        sped_documento as d
                        join sped_natureza_operacao as no on d.natureza_operacao_id=no.id
                    where
                        d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
                """ % (self.dt_ini[:10], self.dt_fim[:10])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for resposta in query_resposta:
            registro_0400 = registros.Registro0400()
            registro_0400.COD_NAT = resposta[0]
            registro_0400.DESCR_NAT = resposta[1]
            lista.append(registro_0400)
        return lista

    def query_registro0200(self):
        query = """
                    select distinct
                        p.id, u.id, di.id, c.id
                    from
                        sped_documento as d
                        join sped_documento_item as di on d.id=di.documento_id
                        join sped_produto as p on di.produto_id=p.id
                        join sped_unidade as u on p.unidade_id=u.id
                        join sped_cfop as c on c.id=di.cfop_id
                    where
                        d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
                   """ % (self.dt_ini[:10], self.dt_fim[:10])

        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        hash = {}
        hash_c170 = {}
        lista = []
        cont = 1
        for resposta in query_resposta:
            resposta_produto = self.env['sped.produto'].browse(resposta[0])
            resposta_unidade = self.env['sped.unidade'].browse(resposta[1])
            resposta_item = self.env['sped.documento.item'].browse(resposta[2])
            resposta_cfop = self.env['sped.cfop'].browse(resposta[3])
            registro_0200 = registros.Registro0200()
            registro_0200.COD_ITEM = resposta_produto.codigo_unico
            registro_0200.DESCR_ITEM = resposta_produto.nome
            registro_0200.COD_BARRA = resposta_produto.codigo_barras
            # registro_0200.COD_ANT_ITEM = query_resposta[0]
            registro_0200.UNID_INV = resposta_unidade.codigo_unico
            registro_0200.TIPO_ITEM = resposta_produto.tipo
            # registro_0200.COD_NCM = query_resposta[0]
            # registro_0200.EX_IPI = query_resposta[0]
            # registro_0200.COD_GEN = query_resposta[0]
            # registro_0200.COD_LST = query_resposta[0]
            # registro_0200.ALIQ_ICMS = query_resposta[0]
            # registro_h005 = registros.RegistroH005()
            # registro_h005.DT_INV = '02022017'
            # registro_h005.VL_INV = '12'
            # registro_h005.MOT_INV = '01'
            if not (resposta_produto.codigo_unico in hash):
                if not (str(resposta_cfop.codigo[1:]) in hash_c170):
                    hash_c170[str(resposta_cfop.codigo[1:])] = self.query_registro_C170(cont, resposta_item, resposta_produto,
                                                  resposta_unidade, resposta_cfop)
                    cont += 1
                    lista.append(self.query_registro_C190(hash_c170[str(resposta_cfop.codigo)[1:]], resposta_item))
                hash[resposta_produto.codigo_unico] = registro_0200
            # lista.append(registro_h005)
        for key,value in hash.items():
            lista.append(value)
        for key, value in hash_c170.items():
            lista.append(value)
        return lista

    def transforma_valor(self, valor):
        return str(valor).replace('.', ',')

    def query_registro_C190(self, registro_c170, documento_item_id):
        registro_c190 = registros.RegistroC190()
        registro_c190.CST_ICMS = registro_c170.CST_ICMS
        registro_c190.CFOP = registro_c170.CFOP[1:]
        registro_c190.ALIQ_ICMS = registro_c170.ALIQ_ICMS
        registro_c190.VL_OPR = str(int(documento_item_id.org_icms) + int(documento_item_id.cst_icms))
        registro_c190.VL_BC_ICMS = '0'
        registro_c190.VL_ICMS = '0'
        registro_c190.VL_BC_ICMS_ST = '0'
        registro_c190.VL_ICMS_ST = '0'
        registro_c190.VL_RED_BC = '0'
        registro_c190.VL_IPI = '0'
        registro_c190.COD_OBS = '0'

        return registro_c190

    def query_registro0175(self):
        registro_0175 = registros.Registro0175()

    def query_registro_C170(self, cont, documento_item, registro_0200,
                            resposta_unidade, resposta_cfop):
        registro_c170 = registros.RegistroC170()
        registro_c170.NUM_ITEM = str(cont)
        registro_c170.COD_ITEM = registro_0200.codigo_unico
        registro_c170.QTD = str(int(documento_item.quantidade))
        registro_c170.UNID = resposta_unidade.codigo_unico
        registro_c170.VL_ITEM = self.transforma_valor(
            str(int(documento_item.vr_unitario) * float(documento_item.vr_produtos)))
        registro_c170.IND_MOV = '0'
        # TODO: criar verificacao se empresa faz parte do simples nacional ou nao
        registro_c170.CST_ICMS = documento_item.cst_icms_sn # TODO: cst_icms_sn ou cst_icms
        if registro_c170.CST_ICMS in ('00','10','20','70'):
            registro_c170.ALIQ_ICMS = str(documento_item.al_icms_proprio) # TODO: analisar com sadamo
        else:
            registro_c170.ALIQ_ICMS = '0' # TODO: analisar com sadamo
        # campo cfop retirar o primeiro digito
        registro_c170.CFOP = str(resposta_cfop.codigo[1:])

        return registro_c170

    def query_registro_C100(self):
        query = """
                    select distinct 
                        d.id, p.id
                    from
                        sped_natureza_operacao n 
                        join sped_documento d on d.natureza_operacao_id = n.id
                        join sped_documento_item as i on d.id=i.documento_id
                        join sped_empresa c on c.id = d.empresa_id
                        join sped_participante p on p.id = c.participante_id
                    where
                        d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
                """ % (self.dt_ini[:10], self.dt_fim[:10])
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for id in query_resposta:
            resposta = self.env['sped.documento'].browse(id[0])
            resposta_participante = self.env['sped.participante'].browse(id[1])
            registro_c100 = registros.RegistroC100()
            registro_c100.IND_OPER = resposta.entrada_saida
            registro_c100.IND_EMIT = resposta.emissao
            registro_c100.COD_PART = str(resposta_participante.id)
            registro_c100.COD_MOD = resposta.modelo
            registro_c100.COD_SIT = resposta.situacao_fiscal

            if resposta.modelo == MODELO_FISCAL_NFE or resposta.modelo == MODELO_FISCAL_NFCE:
                registro_c100.SER = resposta.serie
                registro_c100.CHV_NFE = resposta.chave

            registro_c100.NUM_DOC = self.limpa_formatacao(str(int(resposta.numero)))
            registro_c100.DT_DOC = self.transforma_data(resposta.data_entrada_saida)

            registro_c100.DT_E_S = self.transforma_data(resposta.data_entrada_saida)
            registro_c100.VL_DOC = self.transforma_valor(resposta.vr_nf)
            if resposta.ind_forma_pagamento == '2':
                registro_c100.IND_PGTO = '9'
            else:
                registro_c100.IND_PGTO = resposta.ind_forma_pagamento
            # registro_c100.VL_DESC = resposta
            # registro_c100.VL_ABAT_NT = resposta
            registro_c100.VL_MERC = self.transforma_valor(str(resposta.vr_nf))
            registro_c100.IND_FRT = resposta.modalidade_frete
            # registro_c100.VL_FRT = resposta
            # registro_c100.VL_SEG = resposta
            # registro_c100.VL_OUT_DA = resposta
            # registro_c100.VL_BC_ICMS = resposta
            # registro_c100.VL_ICMS = resposta
            # registro_c100.VL_BC_ICMS_ST = resposta
            # registro_c100.VL_ICMS_ST = resposta
            # registro_c100.VL_IPI = resposta
            # registro_c100.VL_PIS = resposta
            # registro_c100.VL_COFINS = resposta
            # registro_c100.VL_PIS_ST = resposta
            # registro_c100.VL_COFINS_ST = resposta
            lista.append(registro_c100)
        return lista

    # def query_registro_D100(self):
    #     query = """
    #         select distinct
    #             d.id
    #         from
    #             sped_documento as d
    #             join sped_empresa as e on e.id = d.empresa_id
    #             join sped_participante as p on p.id = e.participante_id
    #         where
    #             d.data_entrada_saida>='%s' and data_entrada_saida<='%s'
    #         """ % (self.dt_ini[:10], self.dt_fim[:10])
    #     self._cr.execute(query)
    #     query_resposta = self._cr.fetchall()
    #     lista = []
    #     for id in query_resposta:
    #         resposta = self.env['sped.documento'].browse(id[0])
    #         registro_d100 = registros.RegistroD100()
    #         registro_d100.IND_OPER = resposta.entrada_saida
    #         registro_d100.IND_EMIT = resposta.emissao
    #         registro_d100.COD_PART = '1'
    #         registro_d100.COD_MOD = resposta.modelo
    #         registro_d100.COD_SIT = resposta.situacao_fiscal
    #
    #             registro_d100.SER = resposta.serie
    #         # registro_d100.SUB
    #
    #         registro_d100.NUM_DOC = self.limpa_formatacao(str(resposta.numero))
    #         # registro_d100.CHV_CTE
    #         registro_d100.DT_DOC = self.transforma_data(resposta.data_entrada_saida)
    #         # registro_d100.DT_A_P
    #         # registro_d100.TP_CT-e
    #         # registro_d100.CHV_CTE_REF
    #         registro_d100.VL_DOC = self.limpa_formatacao(str(resposta.vr_produtos))
    #         # registro_d100.VL_DESC
    #         # registro_d100.IND_FRT
    #         registro_d100.VL_SERV = '10' # TODO: achar valor do servico
    #         # registro_d100.VL_BC_ICMS
    #         # registro_d100.VL_ICMS
    #         # registro_d100.VL_NT
    #         # registro_d100.COD_INF
    #         # registro_d100.COD_CTA
    #         lista.append(registro_d100)
    #
    #     return lista

    def query_registro_H005(self):
        query = """

        """
        self._cr.execute(query)
        query_resposta = self._cr.fetchall()
        lista = []
        for id in query_resposta:
            resposta = self.env['sped.documento'].browse(id[0])

    def query_registro_E100(self):
        registro_E100 = registros.RegistroE100()
        registro_E100.DT_INI = self.transforma_data(self.dt_ini[:10])
        registro_E100.DT_FIN = self.transforma_data(self.dt_fim[:10])
        return registro_E100

    def junta_pipe(self, registro):
        junta = ''
        for i in range(1, len(registro._valores)):
            junta = junta + '|' + registro._valores[i]
        return junta

    def envia_efd(self):
        arq = arquivos.ArquivoDigital()
        hash = {}
        hash['0000'] = 1
        hash['9999'] = 1
        # arq.read_registro('|9900|0000|1|')
        # arq.read_registro('|9900|9999|1|')
        # cont_9900 = 2
        # bloco 0
        lista_c170 = []
        lista_c190 = []
        arq.read_registro(self.junta_pipe(self.query_registro0000()))

        arq.read_registro(self.junta_pipe(self.query_registro0005()))

        arq.read_registro(self.junta_pipe(self.query_registro0100()))

        for item_lista in self.query_registro0150():
            arq.read_registro(self.junta_pipe(item_lista))
        # arq.read_registro(self.junta_pipe(self.query_registro0175()))

        for item_lista in self.query_registro0190():
            arq.read_registro(self.junta_pipe(item_lista))

        for item_lista in self.query_registro0200():
            if isinstance(item_lista, registros.RegistroC170):
                lista_c170.append(item_lista)
            elif isinstance(item_lista, registros.RegistroC190):
                lista_c190.append(item_lista)
            else:
                arq.read_registro(self.junta_pipe(item_lista))
        #
        # for item_lista in self.query_registro0400():
        #     arq.read_registro(self.junta_pipe(item_lista))

        # # bloco C
        for item_lista in self.query_registro_C100():
            arq.read_registro(self.junta_pipe(item_lista))
        # for item_lista in lista_c170:
        #     arq.read_registro(self.junta_pipe(item_lista))
        # # for item_lista in lista_c190:
        # #     arq.read_registro(self.junta_pipe(item_lista))
        #
        # # bloco D
        # # for item_lista in self.query_registro_D100():
        # #     arq.read_registro(self.junta_pipe(item_lista))
        #
        # bloco E
        arq.read_registro(self.junta_pipe(self.query_registro_E100()))

        for bloco in arq._blocos.items():
            for registros_bloco in bloco[1].registros:
                if registros_bloco._valores[1] in hash:
                    hash[registros_bloco._valores[1]] = int(hash[registros_bloco._valores[1]]) + 1
                else:
                    hash[registros_bloco._valores[1]] = 1

        for key, value in hash.items():
            registro_9900 = registros.Registro9900()
            registro_9900.REG_BLC = key
            registro_9900.QTD_REG_BLC = str(value)
            arq.read_registro(self.junta_pipe(registro_9900))

        registro_9900 = registros.Registro9900()
        registro_9900.REG_BLC = '9900'
        registro_9900.QTD_REG_BLC = str(len(hash) + 1)
        arq.read_registro(self.junta_pipe(registro_9900))

        arquivo = self.env['ir.attachment']

        dados = {
            'name': 'teste.txt',
            'datas_fname': 'teste.txt',
            'res_model': 'sped.efd',
            'res_id': self.id,
            'datas': base64.b64encode(arq.getstring().encode('utf-8')),
            'mimetype': 'application/txt'
        }
        arquivo.create(dados)