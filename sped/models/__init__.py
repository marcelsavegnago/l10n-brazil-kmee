# -*- coding: utf-8 -*-
#
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 or later (http://www.gnu.org/licenses/agpl)
#

#
# Cópia de views
#
from . import inherited_ir_ui_view

#
# Model Base
#
from . import sped_base

#
# Tabelas Geográficas
#
from . import sped_estado
from . import sped_municipio
#
# Cadastros básicos
#
from . import sped_participante
from . import sped_empresa
from . import inherited_res_partner
#
# Unidade é requisito para NCM e produtos
#
from . import sped_unidade
from . import inherited_product_uom
#
# Tabelas Fiscais
#
from . import sped_cest
from . import sped_cfop
from . import sped_cnae
from . import sped_ncm
from . import sped_servico
from . import sped_nbs
from . import sped_ibptax
from . import sped_ncm_cest
from . import sped_ncm_ibptax

from . import sped_ncm_protocolo
#
# Produtos e serviços
#
from . import sped_produto
from . import inherited_product_template
from . import inherited_product_product

#
# Fiscal e faturamento
#
from . import sped_natureza_operacao
from . import sped_operacao
from . import sped_operacao_item
from . import sped_veiculo
from . import sped_documento
from . import sped_documento_volume
from . import sped_documento_pagamento
from . import sped_documento_duplicata
from . import sped_documento_referenciado
from . import sped_documento_item
from . import sped_documento_item_declaracao_importacao
from . import sped_documento_item_declaracao_importacao_adicao
#
# Parcelamentos e pagamentos
#
from . import copied_account_payment_term
from . import copied_account_payment_term_line
from . import inherited_account_payment_term
