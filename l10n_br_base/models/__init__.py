# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Renato Lima - Akretion
# Copyright 2016 Taŭga Tecnologia
#   Aristides Caldeira <aristides.caldeira@tauga.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
#

from __future__ import division, print_function, unicode_literals

#
# Sincronização de casas decimais
#
from . import inherited_decimal_precision
from . import inherited_res_currency

#
# Templates de email
#
from . import inherited_mail_template

#
# Model Base
#
from . import sped_base

#
# Tabelas Geográficas
#
from . import sped_pais
from . import sped_estado
from . import sped_municipio

#
# Cadastros básicos
#
from . import sped_participante
from . import inherited_res_company
from . import inherited_res_partner
from . import sped_empresa

#
# Parcelamentos e pagamentos; bancos e contas bancárias
#
from . import copied_account_payment_term
from . import copied_account_payment_term_line
from . import inherited_account_payment_term

#
# Unidade é requisito para NCM e produtos
#
from . import sped_unidade
from . import inherited_product_uom

#
# Produtos e serviços
#
from . import sped_produto
from . import inherited_product_template
from . import inherited_product_product
