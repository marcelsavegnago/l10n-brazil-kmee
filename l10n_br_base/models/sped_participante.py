# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#
from odoo import api, fields, models, _


class SpedParticipante(models.Model):
    _name = b'sped.participante'
    _description = 'Participantes'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner original',
        ondelete='restrict',
        required=True,
    )

    @api.multi
    def name_get(self):
        res = []

        for participante in self:
            nome = participante.nome

            if participante.razao_social:
                if participante.nome.strip().upper() != \
                        participante.razao_social.strip().upper():
                    nome += ' - '
                    nome += participante.razao_social

            if participante.cnpj_cpf:
                nome += ' ['
                nome += participante.cnpj_cpf
                nome += '] '

            res.append((participante.id, nome))

        return res