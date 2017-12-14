# -*- encoding: utf-8 -*-

# Copyright (C) 2016 Luiz Felipe do Divino - KMEE - www.kmee.com.br           #
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
import os
import base64
import time
import zipfile
import io


class NfeXmlPeriodicExport(models.TransientModel):
    _inherit = 'nfe.xml.periodic.export'

    zip_sat_file = fields.Binary('Zip SAT', readonly=True)

    @api.multi
    def export(self):
        company = self.create_uid.company_id
        company_has_parent = bool(company.parent_id)

        date_stamp = time.strftime("%Y-%m-%d")
        zipname = 'cfes_xmls_%s' % (date_stamp,)

        pos_order_domain = [
            ('date_order', '>=', self.start_period_id.date_start),
            ('date_order', '<=', self.stop_period_id.date_stop),
            ('cfe_return', '!=', False),
        ]
        if company_has_parent:
            pos_order_domain += [
                ('company_id', '=', company.id),
            ]
            company_name = company.name.replace(" ", "")
            zipname = ('cfes_xmls_%s_%s' % (company_name, date_stamp))

        pos_orders = self.env['pos.order'].search(pos_order_domain)

        if not pos_orders:
            orderFile = io.BytesIO()
            orderZip = zipfile.ZipFile(
                orderFile, mode="w", compression=zipfile.ZIP_DEFLATED
            )

            for pos_order in pos_orders:
                orderZip.writestr(
                    pos_order.chave_cfe + '.xml',
                    base64.b64decode(pos_order.cfe_return),
                )

                if pos_order.cfe_cancelamento_return:
                    orderZip.writestr(
                        pos_order.chave_cfe_cancelamento + '.xml',
                        base64.b64decode(pos_order.cfe_cancelamento_return),
                    )

            orderZip.close()

            itemFile = orderFile.getvalue()

            self.write({
                'state': 'done',
                'zip_sat_file': base64.b64encode(itemFile),
                'name': zipname + '.zip',
            })

        return super(NfeXmlPeriodicExport, self).export()
