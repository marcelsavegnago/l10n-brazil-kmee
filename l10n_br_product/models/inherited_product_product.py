# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

from __future__ import division, print_function, unicode_literals

import logging
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import odoo.addons.decimal_precision as dp
from odoo.addons.l10n_br_base.tools.misc import punctuation_rm
from odoo.addons.l10n_br_base.constante_tributaria import (
    ORIGEM_MERCADORIA,
    TIPO_PRODUTO_SERVICO,
    TIPO_PRODUTO_SERVICO_MATERIAL_USO_CONSUMO,
    TIPO_PRODUTO_SERVICO_SERVICOS,
)

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ProductProduct, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        #
        # Remove a view "estoque" utilizada pelo emissor de nf-e quando
        # o módulo stock do core esta instalado, para evitar conflitos
        #
        if (self.env['ir.module.module'].search_count([
            ('name', '=', 'stock'),
            ('state', '=', 'installed')
        ]) and res.get('type') == 'form'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//page[@name='estoque']"):
                node.getparent().remove(node)
            res['arch'] = etree.tostring(doc)
        return res
