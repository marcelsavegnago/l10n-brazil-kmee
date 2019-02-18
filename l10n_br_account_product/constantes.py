# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATIDA LTDA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import division, print_function, unicode_literals

CAMPO_DOCUMENTO_FISCAL = [
    ('cofins_value', 'COFINS própria'),  # vr_cofins_proprio
    ('cofins_value_wh', 'COFINS retida'),
    ('csll_value', 'CSLL própria'),
    ('csll_value_wh', 'CSLL retida'),
    ('amount_discount', 'Desconto'),
    ('icms_dest_value', 'Diferencial de alíquota (ICMS próprio)'),
    ('amount_freight', 'Frete'),
    ('icms_value', 'ICMS próprio'),  # vr_icms_proprio
    ('icms_st_value', 'ICMS ST'),  # vr_icms_st
    ('ii_value', 'Imposto de importação'),
    ('inss_value_wh', 'INSS retido'),
    ('ipi_value', 'IPI'),  # vr_ipi
    ('irrf_value_wh', 'IRRF retido'),
    ('issqn_value', 'ISS próprio'),
    ('issqn_value_wh', 'ISS retido'),
    ('amount_costs', 'Outras despesas acessórias'),
    ('pis_value', 'PIS próprio'),  # vr_pis_proprio
    ('pis_value_wh', 'PIS retido'),
    ('amount_insurance', 'Seguro'),
    ('amount_net', 'Valor Fatura'),
    ('amount_total', 'Total da NF'),
]

CAMPO_DOCUMENTO_FISCAL_ITEM = (
    'vr_operacao',
    'vr_custo_comercial',
    'vr_custo_estoque',
    'price_total',
)

ACCOUNT_AUTOMATICO = (
    ('CF', 'Cliente/fornecedor'),
    ('PS', 'Produto/serviço'),
)
ACCOUNT_AUTOMATICO_PARTICIPANTE = 'CF'
ACCOUNT_AUTOMATICO_PRODUTO = 'PS'


FORMA_PAGAMENTO = (
    ('01', u'Dinheiro'),
    ('02', u'Cheque'),
    ('03', u'Cartão de crédito'),
    ('04', u'Cartão de débito'),
    ('05', u'Crédito na loja'),
    ('10', u'Vale alimentação'),
    ('11', u'Vale refeição'),
    ('12', u'Vale presente'),
    ('13', u'Vale combustível'),
    ('14', u'Duplicata mercantil'),
    # ('90', u''),
    ('99', u'Outros'),
)
FORMA_PAGAMENTO_DICT = dict(FORMA_PAGAMENTO)

FORMA_PAGAMENTO_DINHEIRO = '01'
FORMA_PAGAMENTO_CHEQUE = '02'
FORMA_PAGAMENTO_CARTAO_CREDITO = '03'
FORMA_PAGAMENTO_CARTAO_DEBITO = '04'
FORMA_PAGAMENTO_CREDITO_LOJA = '05'
FORMA_PAGAMENTO_VALE_ALIMENTACAO = '10'
FORMA_PAGAMENTO_VALE_REFEICAO = '11'
FORMA_PAGAMENTO_VALE_PRESENTE = '12'
FORMA_PAGAMENTO_VALE_COMBUSTIVEL = '13'
FORMA_PAGAMENTO_DUPLICATA_MERCANTIL = '14'
FORMA_PAGAMENTO_OUTROS = '99'

FORMA_PAGAMENTO_CARTOES = (
    FORMA_PAGAMENTO_CARTAO_CREDITO,
    FORMA_PAGAMENTO_CARTAO_DEBITO,
)

BANDEIRA_CARTAO = (
    ('01', u'Visa'),
    ('02', u'Mastercard'),
    ('03', u'American Express'),
    ('04', u'Sorocred'),
    ('05', u'Diners Club'),
    ('06', u'Elo'),
    ('07', u'Hipercard'),
    ('08', u'Aura'),
    ('09', u'Cabal'),
    ('99', u'Outros'),
)
BANDEIRA_CARTAO_DICT = dict(BANDEIRA_CARTAO)

BANDEIRA_CARTAO_VISA = '01'
BANDEIRA_CARTAO_MASTERCARD = '02'
BANDEIRA_CARTAO_AMERICAN_EXPRESS = '03'
BANDEIRA_CARTAO_SOROCRED = '04'
BANDEIRA_CARTAO_DINERS_CLUB = '05'
BANDEIRA_CARTAO_ELO = '06'
BANDEIRA_CARTAO_HIPERCARD = '07'
BANDEIRA_CARTAO_AURA = '08'
BANDEIRA_CARTAO_CABAL = '09'
BANDEIRA_CARTAO_OUTROS = '99'

INTEGRACAO_CARTAO = (
    ('1', 'Integrado'),
    ('2', 'Não integrado'),
)
INTEGRACAO_CARTAO_INTEGRADO = '1'
INTEGRACAO_CARTAO_NAO_INTEGRADO = '2'
