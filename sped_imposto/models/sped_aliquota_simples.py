# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SpedAliquotaSIMPLESAnexo(models.Model):
    _name = b'sped.aliquota.simples.anexo'
    _description = 'Anexos do SIMPLES Nacional'
    _rec_name = 'nome'
    _order = 'nome'

    nome = fields.Char(
        string='Anexo do SIMPLES Nacional',
        size=60,
        index=True
    )
    aliquota_ids = fields.One2many(
        comodel_name='sped.aliquota.simples.aliquota',
        inverse_name='anexo_id',
        string='Alíquotas'
    )

    @api.depends('nome')
    def _check_nome(self):
        for anexo in self:
            if anexo.id:
                anexo_ids = self.search(
                    [('nome', '=', anexo.nome), ('id', '!=', anexo.id)])
            else:
                anexo_ids = self.search([('nome', '=', anexo.nome)])

            if anexo_ids:
                raise ValidationError(
                    _(u'Anexo já existe na tabela!')
                )


class SpedAliquotaSIMPLESTeto(models.Model):
    _name = b'sped.aliquota.simples.teto'
    _description = 'Tetos do SIMPLES Nacional'
    _rec_name = 'nome'
    _order = 'valor'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moeda',
        default=lambda self: self.env.ref('base.BRL').id,
        required=True,
    )
    valor = fields.Monetary(
        string='Valor do teto do SIMPLES Nacional',
        required=True,
        index=True,
    )
    nome = fields.Char(
        string='Teto do SIMPLES Nacional',
        size=40,
        index=True,
    )

    @api.depends('valor')
    def _check_valor(self):
        for teto in self:
            if teto.id:
                teto_ids = self.search(
                    [('valor', '=', teto.valor), ('id', '!=', teto.id)])
            else:
                teto_ids = self.search(
                    [('valor', '=', teto.valor)])
            if teto_ids:
                raise ValidationError('Teto já existe na tabela!')


class SpedAliquotaSIMPLESAliquota(models.Model):
    _name = b'sped.aliquota.simples.aliquota'
    _description = 'Alíquotas do SIMPLES Nacional'
    _rec_name = 'al_simples'
    _order = 'anexo_id, teto_id'

    anexo_id = fields.Many2one(
        comodel_name='sped.aliquota.simples.anexo',
        string='Anexo',
        required=True,
        ondelete='cascade',
    )
    teto_id = fields.Many2one(
        comodel_name='sped.aliquota.simples.teto',
        string='Teto',
        required=True,
        ondelete='cascade',
    )
    al_simples = fields.Float(
        string='SIMPLES',
        digits=(5, 2),
    )
    al_irpj = fields.Float(
        string='IRPJ',
        digits=(5, 2),
    )
    al_csll = fields.Float(
        string='CSLL',
        digits=(5, 2),
    )
    al_cofins = fields.Float(
        string='COFINS',
        digits=(5, 2),
    )
    al_pis = fields.Float(
        string='PIS',
        digits=(5, 2),
    )
    al_cpp = fields.Float(
        string='CPP',
        digits=(5, 2),
    )
    al_icms = fields.Float(
        string='ICMS',
        digits=(5, 2),
    )
    al_iss = fields.Float(
        string='ISS',
        digits=(5, 2),
    )
