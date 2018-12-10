#-*- coding: utf-8 -*-


###########################################################
#Atualiza os novos campos com os dados dos participantes
#criados na sped_documento.
###########################################################

def migrate(cr, version):

    cr.execute('update sped_documento a \
                set \
                    participante_cnpj_cpf = b.cnpj_cpf, \
                    participante_tipo_pessoa = b.tipo_pessoa, \
                    participante_razao_social = b.razao_social, \
                    participante_fantasia = b.fantasia, \
                    participante_endereco = b.endereco, \
                    participante_numero = b.numero, \
                    participante_complemento = b.complemento, \
                    participante_bairro = b.bairro, \
                    participante_municipio_id = b.municipio_id, \
                    participante_cidade = b.cidade, \
                    participante_estado = b.estado, \
                    participante_cep = b.cep, \
                    participante_fone = b.fone, \
                    participante_fone_comercial = b.fone_comercial, \
                    participante_celular = b.celular, \
                    participante_contribuinte = b.contribuinte, \
                    participante_ie = b.ie, \
                    participante_eh_orgao_publico = b.eh_orgao_publico \
                from \
                    sped_participante b \
                where \
                    a.participante_id = b.id;\
                ')
