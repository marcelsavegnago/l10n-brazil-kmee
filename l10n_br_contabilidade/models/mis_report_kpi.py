# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserWarning
import re
from openerp.tools.safe_eval import safe_eval

EXPRESSION_TYPES = [
    ('bal', u'Saldo no período'),
    ('bale', u'Saldo no fim do período'),
    ('bali', u'Saldo no início do período'),
    ('crd', u'Credito no período'),
    ('crdi', u'Crédito no início do período'),
    ('crde', u'Crédito no fim do período'),
    ('deb', u'Débito no período'),
    ('debe', u'Débito no fim do período'),
    ('debi', u'Débito no início do período'),
]

SELECTION_MODE = [
    ('auto', u'Conta Contábil'),
    ('manual', u'Formula'),
]

ACC_RE = re.compile(r"(?P<field>\bbal|\bcrd|\bdeb)"
                    r"(?P<mode>[pise])?"
                    r"(?P<accounts>_[a-zA-Z0-9]+|\[.*?\])"
                    r"(?P<domain>\[.*?\])?"
                    )

MODE_VARIATION = 'p'
MODE_INITIAL = 'i'
MODE_END = 'e'


class MisReportKpi(models.Model):

    _inherit = 'mis.report.kpi'

    @api.depends('style_id')
    def _compute_css_style(self):
        for record in self:
            record.default_css_style = record.style_id.to_css_style(
                record.style_id
            )

    default_css_style = fields.Char(
        compute='_compute_css_style',
        store=True,
    )
    style_id = fields.Many2one(
        comodel_name='mis.report.style',
        string='Estilo',
    )
    account_ids = fields.Many2many(
        comodel_name='account.account',
        inverse_name='mis_report_kpi_ids',
        string='Contas contabeis'
    )
    invert_signal = fields.Boolean(
        default=False,
    )
    expression_type = fields.Selection(
        selection=EXPRESSION_TYPES,
        default='bal'
    )
    expression = fields.Char(
        compute='_compute_kpi_expression_auto_manual',
        store=False,
        required=False,
    )
    expression_manual = fields.Char(
        string='Expressao',
        required=False,
    )
    expression_auto = fields.Char(
        string='Expressao',
        compute='_compute_kpi_expression',
        inverse='_inverse_kpi_expression',
        store=True,
        required=False,
    )
    expression_mode = fields.Selection(
        selection=SELECTION_MODE,
    )
    report_mode = fields.Char(
        # related='report_id.report_mode'
    )

    incluir_lancamentos_de_fechamento = fields.Boolean(
        string=u'Incluir lançamentos de fechamento?'
    )

    @api.one
    @api.onchange('report_mode')
    def onchange_report_mode(self):
        if self.report_mode == 'contabil':
            self.expression_mode = 'auto'
        else:
            self.expression_mode = 'manual'

    @api.one
    @api.constrains('account_ids')
    def _constrains_report_mode(self):
        if self.report_id.report_mode == 'contabil':
            if not self.account_ids and self.expression_mode == 'auto':
                raise UserWarning(
                    u"Não é possível criar um relatório contábil sem "
                    u"preencher as contas da linha"
                )

    def _parse_match_object(self, mo):
        """Split a match object corresponding to an accounting variable

        Returns field, mode, [account codes], (domain expression).
        """
        field, mode, account_codes, domain = mo.groups()
        if not mode:
            mode = MODE_VARIATION
        elif mode == 's':
            mode = MODE_END
        if account_codes.startswith('_'):
            account_codes = account_codes[1:]
        else:
            account_codes = account_codes[1:-1]
        if account_codes.strip():
            account_codes = [a.strip() for a in account_codes.split(',')]
        else:
            account_codes = [None]
        domain = domain or '[]'
        domain = tuple(safe_eval(domain))
        return field, mode, account_codes, domain

    def _onchange_lancamentos_fechamento(self):
        for record in self:
            new_expression = record.expression_manual

            if not new_expression:
                record._compute_kpi_expression()
                continue

            lancamento_de_fechamento_domain = str(
                [('move_id.lancamento_de_fechamento', '=', False)]
            )

            lancamento_fechamento_str = (
                lancamento_de_fechamento_domain
                if not record.incluir_lancamentos_de_fechamento
                else ''
            )

            # removing old existing lancamento_fechamento domain
            expression_wo_domain = new_expression = new_expression.replace(
                lancamento_de_fechamento_domain, '')

            replaced_fields = []
            for exp in ACC_RE.finditer(expression_wo_domain):
                _, mode, account_codes, domain = \
                    self._parse_match_object(exp)

                if not _:
                    record._compute_kpi_expression()
                    continue

                mode_str = mode if mode != MODE_VARIATION else ''
                _str = _ + mode_str

                # Removing custom domains
                if domain:
                    domain_str = '[' + ''.join(str(d) for d in domain) + ']'

                    # Removes the custom domain
                    new_expression = new_expression.replace(domain_str, '')

                field = _str + '[' + ','.join(
                    code for code in account_codes) + ']'

                # Adds the new (or inexisting) domain
                if field not in replaced_fields:
                    new_expression = new_expression.replace(
                        field, field + lancamento_fechamento_str)
                    replaced_fields.append(field)

            record.expression_manual = new_expression

    @api.depends('expression_manual', 'expression_auto', 'expression_mode',
                 'incluir_lancamentos_de_fechamento')
    def _compute_kpi_expression_auto_manual(self):
        for record in self:
            if record.expression_mode == 'manual':
                record._onchange_lancamentos_fechamento()
                record.expression = record.expression_manual
                record.expression_auto = False

            elif record.expression_mode == 'auto':
                record._compute_kpi_expression()
                record.expression = record.expression_auto
                record.expression_manual= False

    @api.depends('account_ids.mis_report_kpi_ids', 'expression_type',
                 'invert_signal')
    def _compute_kpi_expression(self):
        for record in self:
            if record.expression_mode == 'manual':
                record.expression = record.expression_manual
                continue
            if not record.invert_signal and not record.expression_type and not\
                    record.account_ids:
                record.expression_auto = ''
            else:
                signal = ''
                if record.invert_signal:
                    signal = '-'
                record.expression_auto = (
                        signal +
                        record.expression_type +
                        '[{}]'.format(
                            "".join([str(acc.code) + ','
                                     if acc else ''
                                     for acc in record.account_ids])
                        ) + str(
                            [('move_id.lancamento_de_fechamento', '=', False)]
                            if not record.incluir_lancamentos_de_fechamento
                            else ''
                        )
                )

    @api.onchange('expression')
    def _onchange_kpi_expression(self):
        self._inverse_kpi_expression()

    def _test_exp_type(self, exp_t):
        return exp_t if (exp_t in [e[0] for e in EXPRESSION_TYPES]) else False

    def _inverse_kpi_expression(self):
        for record in self:
            if record.expression_mode == 'manual':
                continue

            exp = record.expression

            if not exp:
                continue
            if exp.startswith('-'):
                invert_signal = True
                exp_t = exp[1:].partition('[')[0]
            else:
                invert_signal = False
                exp_t = exp.partition('[')[0]

            if record._test_exp_type(exp_t):
                record.expression_type = record._test_exp_type(exp_t)

                record.invert_signal = invert_signal

                str_account_ids = exp.split('[', 1)[1].split(']')[0]
                account_ids = str_account_ids.split(',')
                record.account_ids = record.env['account.account'].search(
                    [('code', 'in', account_ids)])
            else:
                raise UserWarning(u'Invalid expression type!')
