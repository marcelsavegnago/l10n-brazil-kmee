# -*- coding: utf-8 -*-
# Copyright 2018 KMEE INFORMATICA LTDA - Gabriel Cardoso de Faria
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    cr.execute(
        '''DELETE FROM ir_ui_view WHERE id IN (
        SELECT res_id FROM ir_model_data WHERE name IN (
        'view_l10n_br_base_partner_form', 'view_company_form_inherited'));
        ''')