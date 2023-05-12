import logging
import aiohttp

from datetime import datetime, timedelta

from fastapi import HTTPException
from pydantic import ValidationError

from scheduler.controllers.message import create_message, change_status
from scheduler.exceptions.exceptions import BadResponse

from scheduler.requests import (
    send_message
)

from scheduler.schemas.datatypes import (
    Mailing,
    Message,
)

from scheduler.schemas.message import (
    MessageRequest,
    MessageResponse,
    MessageCreate,
)

MAILING_TIMEOUT = 60 * 1

logger = logging.getLogger('filelogger')


async def mailing_task(
    mailing_task: Mailing,
):
    message_queue = mailing_task.message_queue
    now = datetime.now(message_queue[0].start_window.tzinfo)
    async with aiohttp.ClientSession() as session:
        while message_queue:
            message: Message = message_queue.pop(0)
            context = {
                'field': 'mailing_id', 
                'fieldvalue': mailing_task.id,
            }
            if message.shifted:
                logger.info(
                    'all messages have been shifted. '
                    f'set mailing timeout to {MAILING_TIMEOUT/60} mins',
                    extra=context,
                )
                mailing_task.timeout = now + timedelta(seconds=MAILING_TIMEOUT)
                break
            try:
                if message.start_window < now < message.end_window:
                    message_in_db = await create_message(
                        MessageCreate(
                            mailing_id=mailing_task.id,
                            client_id=message.client_id,
                        )
                    )
                    context['subfield'] = 'message_id'
                    context['subfieldvalue'] = message_in_db.id
                    logger.debug('1/3 message created in database', extra=context)
                    await send_message(
                        MessageRequest(
                            id=message_in_db.id,
                            phone=message.phone,
                            text=mailing_task.body
                        ).dict(),
                    )
                    logger.debug('2/3 message sended', extra=context)
                    await change_status(message_in_db.id, 'sended')
                    logger.info('3/3 message updated status', extra=context)
                else:
                    logger.info(
                        'message can not be send. '
                        'bad time window',
                        extra=context,
                    )
                    continue
            except ValidationError as e:
                logger.exception(
                    f'Validation error catched {e} \n\t\t'
                    'shift message to top',
                    extra=context,
                )
                message.shifted = True
                message_queue.append(message)
            except BadResponse as e:
                logger.exception(
                    f'BadResponse error catched {e} \n\t\t'
                    'shift message to top',
                    extra=context,
                )
                logging.exception(f'body: {await e.response.text()}')
                logging.exception(f'status: {e.status}')
                message.shifted = True
                message_queue.append(message)
            except HTTPException as e:
                logger.exception(
                    f'HTTPException error catched (probably from controller) {e}'
                    '\n\t\tshift message to top',
                    extra=context,
                )
                logger.warning(e.detail())
                message.shifted = True
                message_queue.append(message)
            except Exception as e:
                logger.exception(
                    f'Other Exception catched {e}'
                    '\n\t\tshift message to top',
                    extra=context,
                )
                message.shifted = True
                message_queue.append(message)
