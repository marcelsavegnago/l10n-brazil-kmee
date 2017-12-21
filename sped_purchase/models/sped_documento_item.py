# -*- coding: utf-8 -*-
#
#  Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SpedDocumentoItem(models.Model):
    _inherit = 'sped.documento.item'

    purchase_line_ids = fields.Many2many(
        string='Linha do pedido',
        comodel_name='purchase.order.line',
        copy=False,
    )

    purchase_ids = fields.Many2many(
        string='Pedido de compra',
        comodel_name='purchase.order',
        copy=False,
    )

    pode_alterar_quantidade = fields.Boolean(
        string='Pode alterar a quantidade?',
        compute='_compute_quantidade_alteravel',
        default=True,
    )

    produto_fornecedor_id = fields.Many2one(
        string='Produto de fornecedor',
        comodel_name='sped.produto.fornecedor',
    )

    @api.multi
    def find_lines(self):
        for item in self:
            data = {
                'produto_id': item.produto_id,
                'quantidade': item.quantidade,
                'vr_unitario': item.vr_unitario,
                'vr_frete': item.vr_frete,
                'vr_seguro': item.vr_seguro,
                'vr_desconto': item.vr_desconto,
                'vr_outras': item.vr_outras,
            }
            for linha in item.purchase_ids.mapped('order_line') - \
                    item.mapped('purchase_line_ids'):
                if all(linha[field] == data[field] for field in data.keys()):
                    item.purchase_line_ids += linha

    @api.onchange('purchase_ids', 'purchase_line_ids')
    def _onchange_purchase_line_ids(self):

        for purchase in self.mapped('purchase_ids'):
            if purchase not in self.documento_id.mapped('purchase_order_ids'):
                self.documento_id.purchase_order_ids += purchase

        result = {'domain': {
            'purchase_line_ids': [],
            'purchase_ids': [('invoice_status', '=', 'to invoice')]}}

        if self.purchase_ids:
            result['domain']['purchase_line_ids'].append(
                ('order_id', 'in', self.purchase_ids.ids)
            )

        if self.participante_id:
            result['domain']['purchase_line_ids'].append(
                ('participante_id', '=', self.participante_id.id)
            )
            result['domain']['purchase_ids'].append(
                ('participante_id', '=', self.participante_id.id)
            )

        if self.empresa_id:
            result['domain']['purchase_line_ids'].append(
                ('empresa_id', '=', self.empresa_id.id)
            )
            result['domain']['purchase_ids'].append(
                ('empresa_id', '=', self.empresa_id.id)
            )

        if self.produto_id:
            result['domain']['purchase_line_ids'].append(
                ('produto_id', '=', self.produto_id.id)
            )

        if self.vr_unitario:
            result['domain']['purchase_line_ids'].append(
                ('vr_unitario', '=', self.vr_unitario)
            )

        return result

    @api.constrains('purchase_line_ids', 'quantidade')
    def _check_m2m_quantity(self):
        for item in self:
            if len(item.purchase_line_ids) > 1:
                for linha in item.mapped('purchase_line_ids'):
                    if len(linha.documento_item_ids) > 1:
                        raise ValidationError(_(
                            'Impossível relacionar item de documento com '
                            'linhas de pedido de compras que não tenham '
                            'relação única com esse item.'
                        ))
            elif item.purchase_line_ids:
                total = 0.0
                for doc_item in item.purchase_line_ids.mapped(
                        'documento_item_ids'):
                    total += doc_item.quantidade
                if total > item.purchase_line_ids.quantidade:
                    raise ValidationError(_(
                        'Quantidade do produto ' + item.produto_id.nome +
                        'ultrapassa o disponível na linha do pedido de compra.'
                    ))

    @api.depends('purchase_line_ids')
    def _compute_quantidade_alteravel(self):
        for item in self:
            if len(item.purchase_line_ids) > 1:
                item.pode_alterar_quantidade = False
                quantidade = 0.0
                for linha in item.mapped('purchase_line_ids'):
                    quantidade += linha.quantidade
                item.quantidade = quantidade
            else:
                item.pode_alterar_quantidade = True

    @api.multi
    def selecionar_produto(self):
        return {
            'name': _("Selecionar Produto"),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref(
                'sped_purchase.selecionar_produto_wizard').id,
            'res_model': 'sped.documento.item.selecionar.produto',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_documento_item_id': self.id},
        }

    def _busca_produto_fornecedor(self, dados):
        if dados['codigo_barras']:
            produto = self.env['sped.produto.fornecedor'].search(
                [('codigo_barras', '=', dados['codigo_barras'])])

            if len(produto) == 1:
                produto.write(dados)
                return produto

        produto = self.env['sped.produto.fornecedor'].search(
            [('codigo', '=', dados['codigo'])])

        if len(produto) == 1:
            produto.write(dados)
            return produto

        produto = self.env['sped.produto.fornecedor'].create(dados)

        return produto

    def le_nfe(self, det, dados_documento):
        dados = super(SpedDocumentoItem, self).le_nfe(det, dados_documento)
        if dados.get('produto_id', False):
            return dados
        dados_produto = {
            'codigo': det.prod.cProd.valor,
            'descricao_produto': det.prod.xProd.valor,
            'codigo_barras': det.prod.cEAN.valor,
            'codigo_barras_tributacao': det.prod.cEANTrib.valor,
            'ncm_id': self._busca_ncm(str(det.prod.NCM.valor),
                                      str(det.prod.EXTIPI.valor)),
            'cest_id': self._busca_cest(str(det.prod.CEST.valor)),
            'org_icms': str(det.imposto.ICMS.orig.valor),
            'preco': det.prod.vUnCom.valor,
            'currency_unidade_id': self._busca_unidade(
                det.prod.uCom.valor, False),

        }
        produto_fornecedor = self._busca_produto_fornecedor(dados_produto)
        if produto_fornecedor.produto_id:
            dados['produto_id'] = produto_fornecedor.produto_id.id
        dados['produto_fornecedor_id'] = produto_fornecedor.id
        return dados

    @api.multi
    def write(self, vals):
        res = super(SpedDocumentoItem, self).write(vals)
        for item in self:
            if item.produto_id:
                if not item.produto_fornecedor_id.produto_id:
                    item.produto_fornecedor_id.produto_id = item.produto_id
                elif item.produto_fornecedor_id.produto_id != item.produto_id:
                    item.produto_id =item.produto_fornecedor_id.produto_id
        return res

    @api.model
    def create(self, vals):
        res = super(SpedDocumentoItem, self).create(vals)
        for item in res:
            if item.participante_id and \
                    not item.produto_fornecedor_id.fornecedor:
                item.produto_fornecedor_id = item.participante_id
        return res
