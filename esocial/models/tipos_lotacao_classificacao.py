from odoo import api, fields, models

class TipoLotacaoClassificacao(models.Model):
    _name="esocial.lotacao_classificacao"
    _description = 'Compatibilidade entre Tipos de Lotação e Classificação Tributária'

    name = fields.Char(string='Class. Tributária')
    classificacao_tributaria_ids = fields.Many2many(
        'esocial.lotacao_tributaria', string='Tipos de Lotação Tributária',
        relation='classificacao_tributaria_codigo_ids'
    )

