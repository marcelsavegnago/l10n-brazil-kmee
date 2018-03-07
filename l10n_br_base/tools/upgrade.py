# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


def run(session, logger):
    """Update all modules."""
    if session.is_initialization:
        logger.warn("Usage of upgrade script for initialization detected. "
                    "You should consider customizing the present upgrade "
                    "script to add modules install commands. The present "
                    "script is at : %s (byte-compiled form)",
                    __file__)
        return

    # elif session.db_version < '10.0.0.0.1':
    #     session.update_modules(['all'])
    # elif session.db_version < '10.0.0.0.1':
    #     session.update_modules(['all'])

    update_sped_documento = """
        update sped_documento set partner_id=p.partner_id
        from sped_participante p
        where sped_documento.participante_id = p.id;
        """

    update_res_partner = """update
       res_partner
       set
       (fone, profissao, celular, eh_funcionario, complemento,
        eh_orgao_publico, eh_grupo, eh_consumidor_final, contribuinte,
        suframa, cei, codigo_ans, cep, rg_data_expedicao, municipio_id,
        eh_usuario, rg_orgao_emissor, eh_cliente, eh_convenio, crc,
        email_nfe, create_date, eh_cooperativa, codigo_sindical,
        razao_social, email, regime_tributario, rntrc, tipo_pessoa, cidade,
        eh_empresa, write_date, eh_transportadora, create_uid,
        transportadora_id, nome, message_last_post, cnpj_cpf, eh_fornecedor,
        fone_comercial, codigo, site, im, rg_numero, ie,
        bairro, numero, eh_sindicato, estado, fantasia, crc_uf,
        pais_nacionalidade_id, endereco, date_localization,
        partner_latitude, partner_longitude, condicao_pagamento_id,
        eh_vendedor,cnpj_cpf_raiz, fone_whatsapp, cnpj_cpf_numero) =
        (p.fone, p.profissao, p.celular, p.eh_funcionario,
         p.complemento, p.eh_orgao_publico, p.eh_grupo, p.eh_consumidor_final,
         p.contribuinte, p.suframa, p.cei, p.codigo_ans, p.cep,
         p.rg_data_expedicao, p.municipio_id, p.eh_usuario, p.rg_orgao_emissor,
         p.eh_cliente, p.eh_convenio, p.crc, p.email_nfe, p.create_date,
         p.eh_cooperativa, p.codigo_sindical, p.razao_social,
         p.email, p.regime_tributario, p.rntrc, p.tipo_pessoa, p.cidade,
         p.eh_empresa, p.write_date, p.eh_transportadora, p.create_uid,
         p.transportadora_id, p.nome, p.message_last_post, p.cnpj_cpf,
         p.eh_fornecedor, p.fone_comercial, p.codigo,
         p.site, p.im, p.rg_numero, p.ie, p.bairro, p.numero, p.eh_sindicato,
         p.estado, p.fantasia, p.crc_uf, p.pais_nacionalidade_id, p.endereco,
         p.date_localization, p.partner_latitude,p.partner_longitude,
         p.condicao_pagamento_id, p.eh_vendedor, p.cnpj_cpf_raiz,
         p.fone_whatsapp, p.cnpj_cpf_numero)
       from sped_participante p
       where
       res_partner.id = p.partner_id;
    """

    update_product_template = """WiTH t AS(
    SELECT sp.*, pp.product_tmpl_id as tmpl_id FROM sped_produto as sp
    INNER JOIN product_product pp ON pp.id = sp.product_id
    ) UPDATE product_template SET 
    
    (fator_quantidade_especie, codigo_barras, nome, preco_venda, peso_bruto,
       nome_unico, codigo_unico, org_icms, peso_liquido, marca, preco_custo,
       especie, codigo, unidade_id, tipo, 
       preco_transferencia    
       ) =
        (
        t.fator_quantidade_especie, t.codigo_barras, t.nome, t.preco_venda, t.peso_bruto,
       t.nome_unico, t.codigo_unico, t.org_icms, t.peso_liquido, t.marca, t.preco_custo,
       t.especie, t.codigo, t.unidade_id, t.tipo,
       t.preco_transferencia
      )
        
      from t where product_template.id = t.tmpl_id;"""


    if session.db_version > '10.0.0.0.0':
        session.update_modules(['all'])
