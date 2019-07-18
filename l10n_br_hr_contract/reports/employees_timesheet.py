# -*- coding: utf-8 -*-
# (c) 2019 Kmee - Hugo Borges <hugo.borges@kmee.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime

from openerp import api
from openerp.addons.report_py3o.py3o_parser import py3o_report_extender


class Contrato(object):
    def __init__(self):
        self.idx = ''
        self.matricula_contrato = ''
        self.nome_empregado = ''
        self.cargo = ''
        self.lotacao = ''
        self.ctps_numero = ''
        self.ctps_serie = ''
        self.entrada = ''
        self.intervalo = ''
        self.saida = ''

class Empresa(object):
    def _init_(self):
        self.nome = ''
        self.rua = ''
        self.rua2 = ''
        self.zip = ''
        self.cidade = ''
        self.uf = ''
        self.cnpj = ''
        self.logo = ''
        self.footer = ''

@api.model
@py3o_report_extender(
    'l10n_br_hr_contract.employees_timesheet_py3o_report')
def employees_timesheet(pool, cr, uid, localcontext, context):
    self = localcontext['objects']

    contratos = []
    i = 0
    for contract_id in self.contract_ids:
        contrato = Contrato()
        i = i + 1
        attendance_id = contract_id.working_hours.attendance_ids[:1]
        turno_id = attendance_id.turno_id
        horario_intervalo = attendance_id.turno_id.horario_intervalo_ids[:1]

        contrato.idx = i
        contrato.matricula_contrato = contract_id.matricula_contrato or ''
        contrato.nome_empregado = contract_id.employee_id.name or ''
        contrato.cargo = contract_id.job_id.name or ''
        contrato.lotacao = self.company_id.cod_lotacao or ''
        contrato.ctps_numero = contract_id.employee_id.ctps or ''
        contrato.ctps_serie = contract_id.employee_id.ctps_series or ''
        contrato.entrada = turno_id.hr_entr + 'h' if turno_id else ''
        contrato.intervalo = \
            ('%sh às %sh' %
             (horario_intervalo.ini_interv,
              horario_intervalo.term_interv)) if horario_intervalo else '',
        contrato.saida = turno_id.hr_saida + 'h' if turno_id else ''

        contratos.append(contrato)

    empresa = Empresa()
    empresa.nome = self.company_id.partner_id.name or ''
    empresa.rua = self.company_id.street or ''
    empresa.rua2 = self.company_id.street2 or ''
    empresa.zip = self.company_id.zip or ''
    empresa.cidade = self.company_id.l10n_br_city_id.name or ''
    empresa.uf = self.company_id.state_id.code or ''
    empresa.cnpj = self.company_id.partner_id.cnpj_cpf or ''
    empresa.logo = self.company_id.logo or ''
    empresa.footer = self.company_id.rml_footer or ''

    data = {
        "data_hoje": datetime.now().strftime('%d/%m/%Y'),
        "empresa": empresa,
        "contratos": contratos,
    }

    localcontext.update(data)
