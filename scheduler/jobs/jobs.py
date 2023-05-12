from typing import List

import asyncio

from scheduler.schemas.mailing import MailingInDB
from scheduler.schemas.client import ClientInDB

# from app.db.base import DatabaseManager
from scheduler.controllers.mailing import get_nearest_mailing
from scheduler.controllers.client import get_free_clients

from scheduler.core.alive import AliveMailings
from scheduler.schemas.datatypes import Mailing

from scheduler.tasks.loop import mailing_task

from datetime import datetime, timedelta

import logging
logger = logging.getLogger('filelogger')
SUSPEND_MAILING_ON = 10 * 60


async def check_free_mailing():
    mailings: List[MailingInDB] = await get_nearest_mailing()
    for mailing in mailings:
        if not AliveMailings.mailings.get(mailing.id):
            logging_context = {'field':'mailing_id', 'fieldvalue': mailing.id}
            mailing_task_holder = Mailing(
                id=mailing.id,
                start_at=mailing.start_time,
                end_at=mailing.end_time,
                body=mailing.body,
            )
            AliveMailings.mailings[mailing.id] = mailing_task_holder
            clients: List[ClientInDB] = await get_free_clients(
                mailing.id,
                mailing.return_filter()
            )
            if clients:
                mailing_task_holder.generate_message_queue(clients)
                logging_context['subfield'] = 'messages'
                logging_context['subfieldvalue'] = len(mailing_task_holder.message_queue)
                mailing_task_holder.task = asyncio.create_task(
                    mailing_task(
                        mailing_task_holder
                    )
                )
                logger.info(f'mailing task created', extra=logging_context)
            else:
                logger.info(f'no clients aviable. mailing suspended for {SUSPEND_MAILING_ON/60} minutes', extra=logging_context)
                mailing_task_holder.timeout = datetime.now() + timedelta(seconds=SUSPEND_MAILING_ON)
                AliveMailings.mailings[mailing.id] = mailing_task_holder


async def clean_tasks():
    mailings = AliveMailings.mailings.copy()
    for key in mailings:
        logging_context = {'field':'mailing_id', 'fieldvalue': key}
        mailing_task_holder: Mailing = mailings[key]
        if mailing_task_holder.timeout:
            if datetime.now() < mailing_task_holder.timeout:
                logger.debug(f'await mailing timeout', extra=logging_context)
                continue
            if mailing_task_holder.task:
                mailing_task_holder.task.cancel()
            AliveMailings.mailings.pop(mailing_task_holder.id)
            logger.info(f'cleaning mailing. timeout is ended', extra=logging_context)
            continue
        if not mailing_task_holder.task:
            AliveMailings.mailings.pop(mailing_task_holder.id)
            logger.info(f'cleaning mailing. mailing never started', extra=logging_context)
            continue
        if not mailing_task_holder.task.done():
            logger.info(f'await mailing ending', extra=logging_context)
            continue
        if e:= mailing_task_holder.task.exception():
            logger.exception(f'mailing ended with exception\n{e}', extra=logging_context)
        AliveMailings.mailings.pop(mailing_task_holder.id)
        logger.info(f'cleaning mailing. mailing is ended successfully', extra=logging_context)
