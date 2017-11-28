# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#


import logging

from odoo import _, api, fields, models
import base64
from lxml import objectify

_logger = logging.getLogger(__name__)


class SpedManifestacaoDestinatario(models.Model):
    _name = 'sped.manifestacao.destinatario'
    _description = 'Manifestação do Destinatário'

    empresa_id = fields.Many2one(
        comodel_name='sped.empresa',
        string='Empresa',
        required=True,
    )
    chave = fields.Char(
        string='Chave',
        size=44,
        required=True,
    )
    serie = fields.Char(
        string='Série',
        size=3,
        index=True,
    )
    numero = fields.Float(
        string='Número',
        index=True,
        digits=(18, 0),
    )
    documento_id = fields.Many2one(
        comodel_name='sped.documento',
        string='Documento Fiscal',
    )
    emissor = fields.Char(
        string='Emissor',
        size=60,
    )
    cnpj_cpf = fields.Char(
        string='CNPJ/CPF',
        size=18,
    )
    ie = fields.Char(
        string='Inscrição estadual',
        size=18,
    )
    participante_id = fields.Many2one(
        comodel_name='sped.participante',
        string='Fornecedor',
    )
    data_hora_emissao = fields.Datetime(
        string='Data de emissão',
        index=True,
        default=fields.Datetime.now,
    )
    data_emissao = fields.Date(
        string='Data de emissão',
        compute='_compute_data_hora_separadas',
        store=True,
        index=True,
    )
    hora_emissao = fields.Char(
        'Hora de emissão',
        size=8,
        compute='_compute_data_hora_separadas',
        store=True,
    )
    data_hora_autorizacao = fields.Datetime(
        string='Data de autorização',
        index=True,
    )
    data_autorizacao = fields.Date(
        string='Data de autorização',
        compute='_compute_data_hora_separadas',
        store=True,
        index=True,
    )
    data_hora_cancelamento = fields.Datetime(
        string='Data de cancelamento',
        index=True,
    )
    data_cancelamento = fields.Date(
        string='Data de cancelamento',
        compute='_compute_data_hora_separadas',
        store=True,
        index=True,
    )
    digest_value = fields.Char(
        string='Digest Value',
        size=28,
    )
    justificativa = fields.Char(
        string='Justificativa',
        size=255,
    )
    protocolo_autorizacao = fields.Char(
        string='Protocolo de autorização',
        size=60,
    )
    protocolo_cancelamento = fields.Char(
        string='Protocolo de cancelamento',
        size=60,
    )


    situacao_nfe = fields.Selection(
        string=u'Situacação da NF-e',
        selection=SITUACAO_NFE,
        select=True,
        readonly=True,
    )

    state = fields.Selection(
        string=u'Situacação da Manifestação',
        selection=SITUACAO_MANIFESTACAO,
        select=True,
        readonly=True,
    )
    sped_consulta_dfe_id = fields.Many2one(
        string=u'DF-E',
        comodel_name='sped.consulta.dfe',
        readonly=True,
    )

    @api.multi
    def action_ciencia_emissao(self):
        for record in self:

            record.sped_consulta_dfe_id.validate_nfe_configuration(
                record.empresa_id)

            nfe_result = record.sped_consulta_dfe_id.send_event(
                record.empresa_id,
                record.chave,
                'ciencia_operacao'
            )
            if nfe_result['code'] == '135':
                record.state = 'ciente'
            elif nfe_result['code'] == '573':
                record.state = 'ciente'
            else:
                raise models.ValidationError(
                    nfe_result['code'] + ' - ' + nfe_result['message'])
                return False

        return True

    @api.multi
    def action_confirmar_operacacao(self):
        for record in self:
            record.sped_consulta_dfe_id.validate_nfe_configuration(
                record.empresa_id)
            nfe_result = record.sped_consulta_dfe_id.send_event(
                record.empresa_id,
                record.chave,
                'confirma_operacao')

            if nfe_result['code'] == '135':
                record.state = 'confirmado'
            else:
                raise models.ValidationError(_(
                        nfe_result['code'] + ' - ' + nfe_result['message'])
                )
                return False

        return True

    @api.multi
    def action_operacao_desconhecida(self):
        for record in self:
            record.sped_consulta_dfe_id.\
                validate_nfe_configuration(record.empresa_id)
            nfe_result = record.sped_consulta_dfe_id.send_event(
                record.empresa_id,
                record.chave,
                'desconhece_operacao')

            if nfe_result['code'] == '135':
                record.state = 'desconhecido'
            else:
                raise models.ValidationError(_(
                    nfe_result['code'] + ' - ' + nfe_result['message']))
                return False

        return True

    @api.multi
    def action_negar_operacao(self):
        for record in self:
            record.sped_consulta_dfe_id.\
                validate_nfe_configuration(record.empresa_id)
            nfe_result = record.sped_consulta_dfe_id.send_event(
                record.empresa_id,
                record.chave,
                'nao_realizar_operacao')

            if nfe_result['code'] == '135':
                record.state = 'nap_realizado'
            else:
                raise models.ValidationError(_(
                    nfe_result['code'] + ' - ' + nfe_result['message']))
                return False

        return True

    @api.multi
    def action_download_xml(self):
        result = True
        for record in self:
            record.sped_consulta_dfe_id.\
                validate_nfe_configuration(record.empresa_id)
            nfe_result = record.sped_consulta_dfe_id.\
                download_nfe(record.empresa_id, record.chave)

            if nfe_result['code'] == '138':

                file_name = 'NFe%s.xml' % record.chave
                record.env['ir.attachment'].create(
                    {
                        'name': file_name,
                        'datas': base64.b64encode(nfe_result['nfe']),
                        'datas_fname': file_name,
                        'description':
                            u'XML NFe - Download manifesto do destinatário',
                        'res_model': 'sped.manifestacao.destinatario',
                        'res_id': record.id
                    })

                nfe = objectify.fromstring(nfe_result['nfe'])
                documento = self.env['sped.documento'].new()
                documento.modelo = nfe.NFe.infNFe.ide.mod.text
                documento.le_nfe(xml=nfe_result['nfe'])
            else:
                raise models.ValidationError(_(
                    nfe_result['code'] + ' - ' + nfe_result['message'])
                )

        return result
