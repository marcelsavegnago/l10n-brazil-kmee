# -*- coding: utf-8 -*-
# Copyright 2017 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from __future__ import division, print_function, unicode_literals

from odoo import api, fields, models, _


class SpedObrigacoesFiscais(models.Model):

    _name = b'sped.obrigacoes_fiscais'
    _inherit = ['mail.thread']
    _description = 'Obrigações Fiscais'
    _rec_name = 'mes_ano'

    mes_ano = fields.Char(
        string='Mês e Ano',
    )

    arquivo_zip_xml_nfe_emitidas_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="XML das NF-E's emitidas",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )
    arquivo_zip_xml_nfe_recebidas_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="XML das NF-E's recebidas",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )
    arquivo_zip_xml_cte_recebidas_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="XML das CT-E's recebidos",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )
    arquivo_zip_xml_nfce_cfe_emitidas_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="XML das NFC-E's/CF-E's emitidas",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )
    arquivo_posicao_estoque_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="Posição de estoque",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )
    arquivo_sped_efd_id = fields.Many2one(
        comodel_name='ir.attachment',
        string="SPED EFD/Fiscal",
        ondelete='restrict',
        readonly=True,
        copy=False,
    )

    def gerar_arquivos(self):
        """ Gera todos os arquivos detalhados acima e os coloca em anexo.

        :return:
        """
        raise NotImplementedError

    def _prepara_arquivo_zip_completo(self):
        """ Compacta todos os anexos em um arquivo zip

        :return: zip file
        """
        raise NotImplementedError

    def download_arquivo_zip_completo(self):
        """  Retorna ao usuário o download do arquivo ZIP com os anexos"""
        raise NotImplementedError

    def envia_arquivos_por_email(self):
        """ Envia os arquivos por email, conforme configurações do módulo fiscal"""
        self.ensure_one()
        self.gerar_arquivos()
        zip = self._prepara_arquivo_zip_completo()
        # TODO: Envia o email
        # verificar exemplo em parts.odoo.addons.account.models.account_invoice.AccountInvoice#action_invoice_sent
        # e tb parts.odoo.addons.account.models.account_invoice.MailComposeMessage#send_mail
        raise NotImplementedError
