# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
