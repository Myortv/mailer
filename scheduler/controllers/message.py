from typing import List
from asyncpg import Connection

from scheduler.schemas.message import MessageCreate, MessageInDB

from scheduler.db.base import DatabaseManager as DM

import logging


@DM.acquire_connection()
async def create_message(
    message: MessageCreate,
    conn: Connection = None,
) -> List:
    # logging.info(f'\t\tinside crate message')
    result = await conn.fetchrow(
        'insert into message (status, mailing_id, client_id) values ($1, $2, $3) '
        'on conflict (mailing_id, client_id) do update set status = message.status returning *',  # change on update
        message.status,
        message.mailing_id,
        message.client_id,
    )
    # logging.info(f'\t\tinside create message. message: {result}')
    if not result:
        return
    message = MessageInDB(**result)
    return message


@DM.acquire_connection()
async def change_status(
    id: int,
    status: str,
    conn: Connection = None,
) -> List:
    logging.debug(f'\t\tinside change status')
    result = await conn.fetchrow(
        'update message set status = $1 where $2 = id returning *',
        status,
        id,
    )
    if not result:
        return
    return MessageInDB(**result)
