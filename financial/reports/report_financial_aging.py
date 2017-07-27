# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE INFORMATICA LTDA
#    Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from datetime import datetime, timedelta

from openerp import api, fields
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender
from psycopg2.extensions import AsIs


class Peridos(object):
    def __init__(self, values):
        self.periodo = values['periodo'],
        self.valor = values['valor'],
        self.percentual = values['percentual']


def montar_dicionario_datas_periodos(data_inicial, status, intervalo=30):
    inicio_periodo = 0
    fim_periodo = intervalo
    dicionario_datas_periodos = {}
    data_inicial = fields.Datetime.from_string(data_inicial)
    for num_intervalo in range(7):
        for dia in range(intervalo):
            if num_intervalo < 6:
                day = "0"+str(data_inicial.day) if data_inicial.day < 10 else str(data_inicial.day)
                month = "0"+str(data_inicial.month) if data_inicial.month < 10 else str(data_inicial.month)
                dicionario_datas_periodos.update({
                    str(data_inicial.year)+"-"+month+"-"+day: str(num_intervalo) + str(inicio_periodo) + " - " + str(fim_periodo)
                })
            else:
                dicionario_datas_periodos.update({
                    str(data_inicial.year) + "-" + month + "-" + day: str(num_intervalo) + str(inicio_periodo) + " - "
                })
            if status == "due":
                data_inicial = data_inicial + timedelta(days=1)
            elif status == "overdue":
                data_inicial = data_inicial - timedelta(days=1)
        inicio_periodo = fim_periodo + 1
        fim_periodo += intervalo
    return dicionario_datas_periodos


def totais_por_intervalo(movimentacoes, data_inicial, status, intervalo=30):
    inicio_periodo = 0
    fim_periodo = intervalo
    periodos = {}
    dicionario_datas_periodos = montar_dicionario_datas_periodos(data_inicial, status)
    for i in range(7):
        if i < 6:
            periodos.update({
                str(i) + str(inicio_periodo) + " - " + str(fim_periodo): {
                    'total_periodo': 0.00,
                    'percentual': 0.00,
                }
            })
            inicio_periodo = fim_periodo + 1
            fim_periodo += intervalo
        else:
            periodos.update({
                str(i) + str(inicio_periodo) + " - ": {
                    'total_periodo': 0.00,
                    'percentual': 0.00,
                }
            })

    for movimentacao in movimentacoes:
        periodos[dicionario_datas_periodos[movimentacao[2]]]['total_periodo'] += movimentacao[3]

    return periodos


def buscar_valores_movimentacao_fiscal(movimentacoes, total, data_inicial, status, intervalo=30):
    periodos = totais_por_intervalo(movimentacoes, data_inicial, status)
    for periodo in periodos:
        if periodos[periodo]['total_periodo']:
            periodos[periodo]['percentual'] += (periodos[periodo]['total_periodo']/total) * 100

    return periodos


@api.model
@py3o_report_extender(
    "financial.report_financial_aging_py3o_report")
def financial_aging_report(pool, cr, uid, local_context, context):
    active_model = context['active_model']
    proxy = pool['report.financial.aging.wizard']
    wizard = proxy.browse(cr, uid, context['active_id'])
    SQL_DUE = '''
        SELECT
           fm.id,
           fm.date_document,
           fm.date_business_maturity,
           fm.amount_document,
           fm.amount_paid_discount,
           fm.amount_paid_penalty,
           fm.amount_paid_interest,
           fm.amount_paid_total
        FROM
          financial_move fm
        WHERE
          fm.type = %(type)s
          and fm.debt_status in ('due', 'due_today')
          and fm.date_business_maturity between %(date_from)s and 
                  %(date_to)s
          and fm.state = 'open'
        ORDER BY
          fm.date_business_maturity;
    '''
    date_to = fields.Datetime.from_string(wizard.date_from)
    date_to = date_to + timedelta(days=180)
    date_to = fields.Datetime.to_string(date_to)
    filters = {
        'type': wizard.type,
        'date_from': wizard.date_from,
        'date_to': date_to,
    }
    cr.execute(SQL_DUE, filters)
    data_due = cr.fetchall()
    due_total = 0.00
    for line in data_due:
        due_total += line[3]
    SQL_OVERDUE = '''
                SELECT
                   fm.id,
                   fm.date_document,
                   fm.date_business_maturity,
                   fm.amount_document,
                   fm.amount_paid_discount,
                   fm.amount_paid_penalty,
                   fm.amount_paid_interest,
                   fm.amount_paid_total
                FROM
                  financial_move fm
                WHERE
                  fm.type = %(type)s
                  and fm.debt_status = 'overdue'
                  and fm.date_business_maturity between %(date_from)s and 
                          %(date_to)s
                  and fm.state = 'open'
                ORDER BY
                  fm.date_business_maturity;
            '''
    date_to = fields.Datetime.from_string(wizard.date_from)
    date_to = date_to - timedelta(days=180)
    date_to = fields.Datetime.to_string(date_to)[0:10]
    filters = {
        'type': wizard.type,
        'date_from': date_to[0:10],
        'date_to': wizard.date_from,
    }
    cr.execute(SQL_OVERDUE, filters)
    data_overdue = cr.fetchall()
    overdue_total = 0.00
    for line in data_overdue:
        overdue_total += line[3]

    total_value = overdue_total + due_total
    overdue_total_percentage = (overdue_total/total_value) * 100
    due_total_percentage = (due_total/total_value) * 100

    a_vencer = []
    periodos_due = buscar_valores_movimentacao_fiscal(data_due, total_value, wizard.date_from, "due")
    for periodo_due in sorted(periodos_due.keys()):
        values = {
            'periodo': periodo_due[1:],
            'valor': '%.2f' % periodos_due[periodo_due]['total_periodo'],
            'percentual': '%.2f' % periodos_due[periodo_due]['percentual'],
        }
        a_vencer.append(
            Peridos(values)
        )

    vencido = []
    periodos_overdue = buscar_valores_movimentacao_fiscal(data_overdue, total_value,
                                                  wizard.date_from, "overdue")
    for periodo_overdue in sorted(periodos_overdue.keys()):
        values = {
            'periodo': periodo_overdue[1:],
            'valor': '%.2f' % periodos_overdue[periodo_overdue]['total_periodo'],
            'percentual': '%.2f' % periodos_overdue[periodo_overdue]['percentual'],
        }
        vencido.append(
            Peridos(values)
        )
    data_atual = datetime.now()
    dia = "0" + str(data_atual.day) if data_atual.day < 10 else str(data_atual.day)
    mes = "0" + str(data_atual.month) if data_atual.month < 10 else str(data_atual.month)
    dia_atual = dia + "/" + mes + "/" + str(data_atual.year)
    data = {
        'company': wizard.company_id.display_name,
        'data_atual': dia_atual,
        'vencidos': vencido,
        'total_vencidos': '%.2f' % overdue_total,
        'porcentagem_vencidos': '%.2f' % overdue_total_percentage,
        'avencer': a_vencer,
        'total_avencer': '%.2f' % due_total,
        'porcentagem_avencer': '%.2f' % due_total_percentage,
        'total_geral': total_value,
    }
    local_context.update(data)
