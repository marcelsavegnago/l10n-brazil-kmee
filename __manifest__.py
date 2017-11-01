# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE - Átila Graciano <atilla.silva@kmee.com.br>
# Copyright 2017 KMEE - Bianca Bartolomei <bianca.bartolomei@kmee.com.br>
# Copyright 2017 KMEE - Wagner Pereira <wagner.pereira@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'eSocial - Brasil',
    'summary': """
        Implementa todos os ajustes necessários ao Odoo para suportar os
        serviços do eSocial brasileiro.
        """,
    'version': '11.0.1.0.0',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'author': 'KMEE,Odoo Community Association (OCA)',
    'website': 'www.odoobrasil.org.br',
    'depends': [
        'l10n_br_base',
    ],
    'external_dependencies': {
        'python': [
            'pybrasil',
        ],
    },
    'data': [
        'views/menus.xml',
        'views/codigo_aliquota_FPAS.xml',
        'views/categoria_trabalhador.xml',
        'views/financiamento_aposentadoria.xml',
        'views/natureza_rubrica.xml',
        'views/parte_corpo.xml',
<<<<<<< HEAD
<<<<<<< HEAD
        'views/tipo_inscricao.xml',
=======
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        'views/tipo_inscricao.xml',
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
        'views/agente_causador.xml',
        'views/situacao_geradora_doenca.xml',
        'views/situacao_geradora_acidente.xml',
        'views/natureza_lesao.xml',
<<<<<<< HEAD
<<<<<<< HEAD
        'views/tipo_dependente.xml',
        'views/tipo_lotacao_tributaria.xml',
=======
        'views/tipo_dependente.xml',
<<<<<<< HEAD
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
        'views/classificacao_tributaria.xml',
        'views/motivo_afastamento.xml',
        'views/tipo_arquivo_esocial.xml',
=======
        'views/motivo_afastamento.xml',
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        'views/tipo_lotacao_tributaria.xml',
        'views/classificacao_tributaria.xml',
        'views/motivo_afastamento.xml',
        'views/tipo_arquivo_esocial.xml',
>>>>>>> 84247a3... [ADD] tabelas 9 e 10 feitas
        'views/motivo_desligamento.xml',
        'views/tipo_logradouro.xml',
        'views/natureza_juridica.xml',
        'views/motivo_cessacao.xml',
        'views/tipo_beneficio.xml',
<<<<<<< HEAD
<<<<<<< HEAD
        'views/codificacao_acidente_trabalho.xml',
        'views/fatores_meio_ambiente.xml',
        'data/natureza_lesao.xml',
        'data/codigo_aliquota_FPAS.xml',
        'data/tipo_arquivo_esocial.xml',
        'data/tipo_lotacao_tributaria.xml',
        'data/categoria_trabalhador.xml',
        'data/financiamento_aposentadoria.xml',
        'data/natureza_rubrica.xml',
        'data/tipo_dependente.xml',
        'data/classificacao_tributaria.xml',
        'data/parte_corpo.xml',
        'data/tipo_inscricao.xml',
=======
=======
        'views/codificacao_acidente_trabalho.xml',
>>>>>>> da5aaac... [ADD]Módulo 24
        'data/natureza_lesao.xml',
        'data/categoria_trabalhador.xml',
        'data/financiamento_aposentadoria.xml',
        'data/natureza_rubrica.xml',
        'data/tipo_dependente.xml',
        'data/classificacao_tributaria.xml',
        'data/parte_corpo.xml',
<<<<<<< HEAD
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        'data/tipo_inscricao.xml',
>>>>>>> 919ddf3... [ADD] tabelas 5,7 e 8 e algumas correcoes
        'data/agente_causador.xml',
        'data/situacao_geradora_doenca.xml',
        'data/situacao_geradora_acidente.xml',
        'data/natureza_lesao.xml',
        'data/motivo_afastamento.xml',
        'data/motivo_desligamento.xml',
        'data/tipo_logradouro.xml',
        'data/natureza_juridica.xml',
        'data/motivo_cessacao.xml',
        'data/tipo_beneficio.xml',
<<<<<<< HEAD
<<<<<<< HEAD
        'data/codificacao_acidente_trabalho.xml',
        'data/fatores_meio_ambiente.xml'
=======
>>>>>>> c7e221e... [ADD] Tabelas eSocial 01, 02, 03, 13, 14, 15, 16, 17, 18 , 19, 20 , 21, 25 e 26
=======
        'data/codificacao_acidente_trabalho.xml',
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> da5aaac... [ADD]Módulo 24
=======
        'data/fatores_meio_ambiente.xml'
>>>>>>> 68e66ce... [ADD]Módulo 23
=======
        'data/fatores_meio_ambiente.xml',

         'security/esocial_security.xml',
         'security/ir.model.access.csv',
>>>>>>> 2af478f... [ADD] permissoes, todos as tabelas
    ],
    'application': True,
}
