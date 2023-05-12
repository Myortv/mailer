from fastapi import HTTPException

from pydantic import ValidationError

import asyncpg

import logging

from scheduler.utils.exceptions import raise_exception
logger = logging.getLogger('filelogger')


class DatabaseManager:
    POOL: asyncpg.Pool = None

    @classmethod
    async def start(
        cls,
        database: str,
        user: str,
        password: str,
        host: str,
    ) -> None:
        cls.POOL = await asyncpg.create_pool(
            database=database,
            user=user,
            password=password,
            host=host,
        )
        logging.info(f'DatabaseManager create postgres pool on:{cls.POOL}')

    @classmethod
    async def stop(cls):
        await cls.POOL.close()
        logging.info(f'DatabaseManager stops postgres pool on:{cls.POOL}')



    @classmethod
    def acquire_connection(cls):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                async with cls.POOL.acquire() as conn:
                    try:
                        result = await func(*args, conn=conn, **kwargs)
                        return result
                    except ValidationError as e:
                        logger.exception(
                            'Validation error catched in acquire_connection. '
                            f'called func ({func})'
                            f'{args} {kwargs} {e}'
                        )
                    except HTTPException as e:
                        logger.exception(
                            'HTTPException error catched in acquire_connection. '
                            f'called func ({func})'
                            f'{args} {kwargs} {e}'
                        )
                    except Exception as e:
                        logger.exception(
                            'General error catched in acquire_connection. '
                            f'called func ({func})'
                            f'{args} {kwargs} {e}'
                        )
            return wrapper
        return decorator
