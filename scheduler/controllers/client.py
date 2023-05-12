from typing import List, Dict
from asyncpg import Connection
from fastapi import HTTPException

from scheduler.schemas.client import ClientInDB, ClientFliter, FreeClientInDB

from scheduler.db.base import DatabaseManager as DM

# import logging


def unpack_data(data):
    if isinstance(data, dict):
        fields = list(data.keys())
        values = list(data.values())
        return fields, values
    fields = list(data.__dict__.keys())
    values = list(data.__dict__.values())
    assert len(fields) == len(values)
    return (fields, values)

def generate_placeholder(data, i=0):
    pair = ''
    values_out = []
    fields, values = unpack_data(data)
    for j, field in enumerate(fields):
        if values[j] is not None:
            i += 1
            pair += f' and {field} = ${i} '
            values_out.append(values[j])
    return pair, values_out


@DM.acquire_connection()
async def get_free_clients(
    mailing_id: int,
    filters: ClientFliter,
    conn: Connection = None,
) -> List:
    placeholder, values = generate_placeholder(filters, i=1)
    # logging.info(f'\t\tinside get free clients. placeholder: {placeholder}')
    result = await conn.fetch(
        'select '
            'id, '
            'mobile_operator_code, '
            'tag, '
            'timezone, '
            '(start_recieve + now()::date) at time zone timezone as start_recieve, '
            'recieve_duration, '
            'phone_number '
        'from '
        'available_clients '
            'where ('
                "id in ("
                    "select client_id from message where message.status != 'await' "
                ") and "
                "$1 in ("
                    "select mailing_id from message where message.status != 'await' "
                ") "
            ") = false "
            f"{placeholder} ",
        mailing_id,
        *values
    )
    # logging.info(f'\t\tinside get free clients. placeholder: {placeholder}')
    # logging.info(f'\t\tinside get free clients. clients: {result}')
    if not result:
        return
    clients = [FreeClientInDB(**client) for client in result]
    return clients
