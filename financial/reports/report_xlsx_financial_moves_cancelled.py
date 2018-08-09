# -*- coding: utf-8 -*-
#
# Copyright 2017 KMEE INFORMATICA LTDA
#    Luiz Felipe do Divino <luiz.divino@kmee.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

from openerp import _
from openerp import fields
from openerp.report import report_sxw
from psycopg2.extensions import AsIs

from .report_xlsx_financial_base import ReportXlsxFinancialBase


class ReportXslxFinancialMovesCancelled(ReportXlsxFinancialBase):
    def define_title(self):
        title = _('Report Moves Cancelled')

        return title

    def define_filters(self):
        date_from = fields.Datetime.from_string(self.report_wizard.date_from)
        date_from = date_from.date()
        date_to = fields.Datetime.from_string(self.report_wizard.date_to)
        date_to = date_to.date()

        filters = {
            0: {
                'title': _('Date'),
                'value': _('From %s to %s') %
                (date_from.strftime('%d/%m/%Y'),
                 date_to.strftime('%d/%m/%Y')),
            },
            1: {
                'title': _('Company'),
                'value': self.report_wizard.company_id.name,
            },

        }
        return filters

    def define_filter_title_column_span(self):
        return 2

    def define_filter_value_column_span(self):
        return 3

    def prepare_data(self):
        #
        # First, we prepare the report_data lines, time_span and accounts
        #
        report_data = {
            'lines': {},
            'total_lines': {},
        }
        SQL_INICIAL_VALUE = '''
           SELECT
              fm.id,
              fm.date_cancel,
              pa.name,
              pa.cnpj_cpf,
              fm.amount_paid_total,
              fm.date_business_maturity,
              fm.document_number,
              fm.amount_document,
              fm.partner_id,
              fm.%(group_by)s
           FROM
             financial_move fm
             join res_partner pa on pa.id = fm.partner_id
           WHERE
             fm.type = %(type)s and
             fm.date_cancel between %(date_from)s and 
             %(date_to)s
             and fm.state = 'cancelled'
           ORDER BY
             fm.%(group_by)s;
       '''
        filters = {
            'group_by': AsIs('motivo_cancelamento_id'),
            'type': self.report_wizard.type,
            'date_to': self.report_wizard.date_to,
            'date_from': self.report_wizard.date_from,
        }
        self.env.cr.execute(SQL_INICIAL_VALUE, filters)
        data = self.env.cr.fetchall()
        for line in data:
            line_dict = {
                'dt_baixa': line[1],
                'cliente': line[2],
                'cnpj_cpf': line[3],
                'vlr_baixado': line[4],
                'dt_vencimento': line[5],
                'num_documento': line[6],
                'vlr_contrato': line[7],
            }
            if report_data['lines'].get(line[9]):
                report_data['lines'][line[9]].append(line_dict)
            else:
                report_data['lines'][line[9]] = [line_dict]
        SQL_VALUE = '''
            SELECT
               fm.%(group_by)s,
               sum(fm.amount_paid_total) as amount_paid_total,
               sum(fm.amount_document) as amount_document
            FROM
                financial_move fm
                join res_partner pa on pa.id = fm.partner_id
            WHERE
             fm.type = %(type)s and
             fm.date_cancel between %(date_from)s and 
             %(date_to)s
             and fm.state = 'cancelled'
            GROUP BY
              fm.%(group_by)s
            ORDER BY
              fm.%(group_by)s;
        '''
        filters = {
            'group_by': AsIs('motivo_cancelamento_id'),
            'type': self.report_wizard.type,
            'date_to': self.report_wizard.date_to,
            'date_from': self.report_wizard.date_from,
        }
        self.env.cr.execute(SQL_VALUE, filters)
        data = self.env.cr.fetchall()
        for line in data:
            line_dict = {
                'vlr_baixado': line[1],
                'vlr_contrato': line[2],
            }
            report_data['total_lines'][line[0]] = line_dict
        return report_data

    def define_columns(self):
        result = {
            0: {
                'header': _('Dt. Baixa'),
                'field': 'dt_baixa',
                'width': 10,
                'style': 'date',
                'type': 'date',
            },
            1: {
                'header': _('Cliente'),
                'field': 'cliente',
                'width': 50,
            },
            2: {
                'header': _('CNPJ/CPF'),
                'field': 'cnpj_cpf',
                'width': 18,
            },
            3: {
                'header': _('Vlr. Baixado'),
                'field': 'vlr_baixado',
                'width': 10,
                'style': 'currency',
                'type': 'currency',
            },
            4: {
                'header': _('Dt. Venc.'),
                'field': 'dt_vencimento',
                'width': 10,
                'style': 'date',
                'type': 'date',
            },
            5: {
                'header': _('Nº Documento'),
                'field': 'num_documento',
                'width': 18,
            },
            6: {
                'header': _('Vlr. Contrato'),
                'field': 'vlr_contrato',
                'width': 10,
                'style': 'currency',
                'type': 'currency',
            },
        }

        return result

    def define_columns_summary_total(self):
        result = {
            3: {
                'header': _('Vlr. Baixado'),
                'field': 'vlr_baixado',
                'width': 10,
                'style': 'currency',
                'type': 'currency',
            },
            6: {
                'header': _('Vlr. Contrato'),
                'field': 'vlr_contrato',
                'width': 10,
                'style': 'currency',
                'type': 'currency',
            },
        }
        return result

    def write_content(self):
        self.sheet.set_zoom(85)

        for move_id in sorted(self.report_data['lines'].keys()):
            motivo = self.env['financial.move.motivo.cancelamento'].browse(
                move_id).motivo_cancelamento
            self.sheet.merge_range(
                self.current_row, 0,
                self.current_row + 1,
                len(self.columns) - 1,
                _('Motivo Baixa: ' + motivo),
                self.style.header.align_left
            )
            self.current_row += 1
            self.write_header()

            line_position = 0
            for line in self.report_data['lines'][move_id]:
                self.write_detail(line)
                line_position += 1

            self.sheet.merge_range(
                self.current_row, 0,
                self.current_row + 1,
                len(self.columns) - 1,
                _('Total - Motivo Baixa: ' + motivo),
                self.style.header.align_left
            )
            self.current_row += 1
            self.write_header()
            self.write_detail(self.report_data['total_lines'][move_id])
            self.current_row += 1

        self.current_row += 1
        self.sheet.merge_range(
            self.current_row, 0,
            self.current_row + 1,
            len(self.columns) - 1,
            _('Total Geral'),
            self.style.header.align_left
        )
        self.current_row += 1
        self.write_header()
        total_columns = self.define_columns_summary_total()
        total_geral_dict = {
            'vlr_baixado': 0.00,
            'vlr_contrato': 0.00,
        }
        for total in self.report_data['total_lines']:
            total_geral_dict['vlr_baixado'] += \
                float(self.report_data['total_lines'][total]['vlr_baixado'])
            total_geral_dict['vlr_contrato'] += \
                float(self.report_data['total_lines'][total]['vlr_contrato'])
        first_data_row = self.current_row + 1
        self.write_detail(total_geral_dict, total_columns,
                          first_data_row)

    def generate_xlsx_report(self, workbook, data, report_wizard):
        super(ReportXslxFinancialMovesCancelled, self).generate_xlsx_report(
            workbook, data, report_wizard)

        workbook.set_properties({
            'title': self.title,
            'company': self.report_wizard.company_id.name,
            'comments': _('Created with Financial app on {now}').format(
                now=fields.Datetime.now())
        })

        #
        # Documentation for formatting pages here:
        # http://xlsxwriter.readthedocs.io/page_setup.html
        #
        self.sheet.set_landscape()
        self.sheet.set_paper(9)  # A4
        self.sheet.fit_to_pages(1, 99999)
        #
        # Margins, in inches, left, right, top, bottom;
        # 1 / 2.54 = 1 cm converted in inches
        #
        self.sheet.set_margins(1 / 2.54, 1 / 2.54, 1 / 2.54, 1 / 2.54)


ReportXslxFinancialMovesCancelled(
    #
    # Name of the report in report_xlsx_financial_cashflow_data.xml,
    # field name, *always* preceeded by "report."
    #
    'report.report_xlsx_financial_moves_cancelled',
    #
    # The model used to filter report data, or where the data come from
    #
    'report.xlsx.financial.moves.cancelled.wizard',
    parser=report_sxw.rml_parse
)
