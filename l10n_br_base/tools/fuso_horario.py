# -*- coding: utf-8 -*-
# Copyright (C) 2018  Gabriel Cardoso de Faria - KMEE
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from __future__ import (division, print_function, unicode_literals,
                        absolute_import)


from past.builtins import basestring
from pytz import (datetime, timezone, UTC)
from datetime import datetime as datetime_sem_fuso, date, time
from dateutil.relativedelta import relativedelta
from pybrasil.data.parse_datetime import parse_datetime
from pybrasil.data.fuso_horario import fuso_horario_sistema

FUSOS_HORARIOS = {
    'AC': timezone('America/Rio_Branco'),
    'AL': timezone('America/Maceio'),
    'AM': timezone('America/Manaus'),
    'AP': timezone('America/Belem'),
    'BA': timezone('America/Bahia'),
    'CE': timezone('America/Fortaleza'),
    'DF': timezone('America/Sao_Paulo'),
    'ES': timezone('America/Sao_Paulo'),
    'GO': timezone('America/Sao_Paulo'),
    'MA': timezone('America/Fortaleza'),
    'MG': timezone('America/Sao_Paulo'),
    'MS': timezone('America/Campo_Grande'),
    'MT': timezone('America/Cuiaba'),
    'PA': timezone('America/Belem'),
    'PB': timezone('America/Fortaleza'),
    'PE': timezone('America/Recife'),
    'PI': timezone('America/Fortaleza'),
    'PR': timezone('America/Sao_Paulo'),
    'RJ': timezone('America/Sao_Paulo'),
    'RN': timezone('America/Fortaleza'),
    'RO': timezone('America/Porto_Velho'),
    'RR': timezone('America/Boa_Vista'),
    'RS': timezone('America/Sao_Paulo'),
    'SC': timezone('America/Sao_Paulo'),
    'SE': timezone('America/Maceio'),
    'SP': timezone('America/Sao_Paulo'),
    'TO': timezone('America/Araguaina'),
}


def data_hora_horario_local(data, estado=None):
    if isinstance(data, basestring):
        data = parse_datetime(data)

    if not isinstance(data,
                      (datetime.datetime, datetime_sem_fuso, date, time)):
        return None

    if isinstance(data, datetime.datetime):
        if not data.tzinfo:
            data = fuso_horario_sistema().localize(data)

    elif isinstance(data, date):
        #
        # Ajusta date para datetime ao meio-dia,
        # pra não voltar a data pro dia anterior
        # Define depois a hora para meia-noite
        #
        data = datetime_sem_fuso(data.year, data.month, data.day, 12, 0, 0, 0)
        data = data_hora_horario_local(data)
        data = data + relativedelta(hour=0, minute=0, second=0, microsecond=0)
        return data

    elif isinstance(data, time):
        #
        # Hora sem data, assume a data de hoje
        #
        hora = data
        data = datetime.datetime.now()
        data = data_hora_horario_local(data)
        data = data + relativedelta(
            hour=hora.hour, minute=hora.minute,
            second=hora.second, microsecond=hora.microsecond
        )
        return data

    elif isinstance(data, datetime_sem_fuso):
        data = fuso_horario_sistema().localize(data)

    data = UTC.normalize(data)
    data = FUSOS_HORARIOS.get(
        estado, timezone('America/Sao_Paulo')
    ).normalize(data)
    return data
