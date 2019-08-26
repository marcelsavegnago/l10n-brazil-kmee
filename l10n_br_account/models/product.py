# -*- coding: utf-8 -*-
# Copyright (C) 2009  Gabriel C. Stabel
# Copyright (C) 2009 - TODAY Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, fields
from .l10n_br_account import PRODUCT_FISCAL_TYPE, PRODUCT_FISCAL_TYPE_DEFAULT

TIPO_PRODUTO_REVENDA = '00'
TIPO_PRODUTO_MATERIA_PRIMA = '01'
TIPO_PRODUTO_EMBALADEM = '02'
TIPO_PRODUTO_EM_PROCESSO = '03'
TIPO_PRODUTO_ACABADO = '04'
TIPO_PRODUTO_SUBPRODUTO = '05'
TIPO_PRODUTO_INTERMEDIARIO = '06'
TIPO_PRODUTO_USO_CONSUMO = '07'
TIPO_PRODUTO_IMOBILIZADO = '08'
TIPO_PRODUTO_SERVICOS = '09'
TIPO_PRODUTO_INSUMO = '10'
TIPO_PRODUTO_OUTROS = '99'

TIPO_PRODUTO = [
    TIPO_PRODUTO_REVENDA,
    TIPO_PRODUTO_MATERIA_PRIMA,
    TIPO_PRODUTO_EMBALADEM,
    TIPO_PRODUTO_EM_PROCESSO,
    TIPO_PRODUTO_ACABADO,
    TIPO_PRODUTO_SUBPRODUTO,
    TIPO_PRODUTO_INTERMEDIARIO,
    TIPO_PRODUTO_USO_CONSUMO,
    TIPO_PRODUTO_IMOBILIZADO,
    TIPO_PRODUTO_INSUMO,
    TIPO_PRODUTO_OUTROS,
]

TIPO_PRODUTO_NAO_IMOBILIZADO = TIPO_PRODUTO[:]
TIPO_PRODUTO_NAO_IMOBILIZADO.remove(TIPO_PRODUTO_IMOBILIZADO)

TIPO_SERVICO = [
    TIPO_PRODUTO_SERVICOS,
]

SELECTION_TIPO_PRODUTO = [
    (TIPO_PRODUTO_REVENDA, 'Mercadoria para Revenda'),
    (TIPO_PRODUTO_MATERIA_PRIMA, 'Matéria-Prima'),
    (TIPO_PRODUTO_EMBALADEM, 'Embalagem'),
    (TIPO_PRODUTO_EM_PROCESSO, 'Produto em Processo'),
    (TIPO_PRODUTO_ACABADO, 'Produto Acabado'),
    (TIPO_PRODUTO_SUBPRODUTO, 'Subproduto'),
    (TIPO_PRODUTO_INTERMEDIARIO, 'Produto Intermediário'),
    (TIPO_PRODUTO_USO_CONSUMO, 'Material de Uso e Consumo'),
    (TIPO_PRODUTO_IMOBILIZADO, 'Ativo Imobilizado'),
    (TIPO_PRODUTO_SERVICOS, 'Serviços'),
    (TIPO_PRODUTO_INSUMO, 'Outros Insumos'),
    (TIPO_PRODUTO_OUTROS, 'Outros'),
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('tipo_item')
    def _compute_fiscal_type(self):
        for record in self:
            if record.tipo_item:
                if record.tipo_item == TIPO_PRODUTO_SERVICOS:
                    record.fiscal_type = 'service'
                else:
                    record.fiscal_type = 'product'

            if record.tipo_item == TIPO_PRODUTO_IMOBILIZADO:
                record.eh_imobilizado = True
            else:
                record.eh_imobilizado = False

    fiscal_category_default_ids = fields.One2many(
        'l10n_br_account.product.category', 'product_tmpl_id',
        u'Categoria de Operação Fiscal Padrões')
    service_type_id = fields.Many2one(
        'l10n_br_account.service.type', u'Tipo de Serviço')
    fiscal_type = fields.Selection(
        PRODUCT_FISCAL_TYPE,
        'Tipo Fiscal',
        compute='_compute_fiscal_type',
        store=True,
        track_visibility='onchange',
    )
    tipo_item = fields.Selection(
        help="Tipo do item – Atividades Industriais, Comerciais e Serviços",
        selection=SELECTION_TIPO_PRODUTO,
        track_visibility='onchange',
        string='Tipo Item'
    )
    eh_imobilizado = fields.Boolean(
        compute='_compute_fiscal_type',
        store=True,
        readonly=True,
    )


class L10nBrAccountProductFiscalCategory(models.Model):
    _name = 'l10n_br_account.product.category'

    fiscal_category_source_id = fields.Many2one(
        'l10n_br_account.fiscal.category', 'Categoria de Origem')
    fiscal_category_destination_id = fields.Many2one(
        'l10n_br_account.fiscal.category', 'Categoria de Destino')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Produto', ondelete='cascade')
    to_state_id = fields.Many2one(
        'res.country.state', 'Estado Destino')
