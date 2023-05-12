import ujson
import logging
import aiohttp

from scheduler.schemas.message import MessageResponse

from scheduler.core.configs import settings

from scheduler.exceptions.exceptions import (
        BadResponse
    )

logger = logging.getLogger('filelogger')


async def send_message(
    data: dict,
    url: str = settings.MAILING_SERVER_URL,
    auth_token: str = settings.AUTHTOKEN,
):
    headers = dict()
    headers['Authorization'] = f'Bearer {auth_token}'
    headers['accept'] = 'application/json'
    headers['Content-Type'] = 'application/json'
    body = ujson.dumps(data)
    url = f"{url}{data['id']}"
    logger.debug(f'send message.\t\turl: {url}\t\theaders: {headers}')
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=data,
        ) as response:
            if response.status != 200:
                raise BadResponse(response)
            return MessageResponse.parse_raw(await response.text())
