# -*- coding: utf-8 -*-
# Copyright 2018 Kmee Informática
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class CrmToNfe(TransactionCase):

    def setUp(self):
        super(CrmToNfe, self).setUp()

        # TODO: cadastro da empresa
        # TODO: cadastro de cliente
        # TODO: criar registro de CRM

    def test_create_oportunity(self):

        # TODO: CRM -> oportunidade

        self.assertEqual(
            # self.crm.state == 'opportunity'
            1, 1
        )

    def test_opportunity_to_sale(self):

        # TODO: oportunidade -> venda

        self.assertEqual(
            # all(self.crm._fields == self.sale._fields)
            1, 1
        )

    def test_sale_to_picking(self):

        # TODO: venda -> separação de estoque

        self.assertEqual(
            # all(self.sale.order_line == self.picking.move_lines)
            1, 1
        )

    def test_picking_to_invoice(self):

        # TODO separação de estoque -> nota fiscal

        self.assertEqual(
            # all(self.sale._fields == self.nfe._fields)
            # all(self.sale.order_line == self.nfe.item_ids)
            1, 1
        )
