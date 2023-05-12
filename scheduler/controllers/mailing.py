import ujson
from fastapi import HTTPException
from asyncpg import Connection

from scheduler.schemas.mailing import MailingInDB

from scheduler.db.base import DatabaseManager as DM



@DM.acquire_connection()
async def get_nearest_mailing(
    conn: Connection = None,
):
    await conn.set_type_codec(
        'json',
        encoder=ujson.dumps,
        decoder=ujson.loads,
        schema='pg_catalog',
    )

    result = await conn.fetch(
        '''select
            *
        from
            mailing
        where
            (
                mailing.end_time is not null and
                now() between
                    mailing.start_time
                        and
                    mailing.end_time
            ) or (
                now() > mailing.start_time and
                mailing.end_time is null
            )'''
        )
    if not result:
        return
    mailings = [MailingInDB(**mailing) for mailing in result]
    return mailings
