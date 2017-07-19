# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATIDA LTDA
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import division, print_function, unicode_literals

CAMPO_DOCUMENTO_FISCAL = [
    ('cofins_value', 'COFINS própria'),  # vr_cofins_proprio
    ('cofins_value_wh', 'COFINS retida'),
    ('csll_value', 'CSLL própria'),
    ('csll_value_wh', 'CSLL retida'),
    ('discount_value', 'Desconto'),
    ('icms_dest_value', 'Diferencial de alíquota (ICMS próprio)'),
    ('freight_value', 'Frete'),
    ('icms_value', 'ICMS próprio'),  # vr_icms_proprio
    ('icms_st_value', 'ICMS ST'),  # vr_icms_st
    ('ii_value', 'Imposto de importação'),
    ('inss_value_wh', 'INSS retido'),
    ('ipi_value', 'IPI'),  # vr_ipi
    ('irrf_value_wh', 'IRRF retido'),
    ('issqn_value', 'ISS próprio'),
    ('issqn_value_wh', 'ISS retido'),
    ('other_costs_value', 'Outras despesas acessórias'),
    ('pis_value', 'PIS próprio'),  # vr_pis_proprio
    ('pis_value_wh', 'PIS retido'),
    ('insurance_value', 'Seguro'),
    ('amount_net', 'Total da fatura'),
    ('price_total', 'Total da NF'),
    ('vr_operacao', 'Valor da operação'),
    ('vr_custo_comercial', '# Custo (nas entradas/compras)'),
    ('vr_custo_estoque', '# Custo médio (nas saídas/vendas)'),
    # ('vr_icms_sn', '# Crédito de ICMS - SIMPLES Nacional'),
    # ('vr_diferencial_aliquota_st', '# Diferencial de alíquota (ICMS ST)'),
    # ('vr_irpj_proprio', '# IRPJ próprio'),
    # ('vr_simples', '# SIMPLES'),
]

CAMPO_DOCUMENTO_FISCAL_ITEM = (
    'vr_operacao',
    'vr_custo_comercial',
    'vr_custo_estoque',
    'price_total',
)
