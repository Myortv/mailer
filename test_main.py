from asyncpg.exceptions import DuplicateDatabaseError
from fastapi.testclient import TestClient

from .core.configs import settings

from .main import app
from .db.base import DatabaseManager

import logging


START_TEST = True

client = TestClient(app)


async def override_dependency():
    return True

app.dependency_overrides[settings.AUTH.get_user] = override_dependency


@app.on_event('startup')
async def swap_to_test_db():
    logging.info('swaping database connection')
    await DatabaseManager.start(
        'temp_mailing',
        settings.POSTGRES_USER,
        settings.POSTGRES_PASSWORD,
        settings.POSTGRES_HOST,
    )
    async with DatabaseManager.POOL.acquire() as conn:
        await conn.execute(
            f"SELECT truncate_tables('{settings.POSTGRES_USER}');"
        )


def test_get_all_client():
    response = client.get(
        '/client/admin/all'
    )
    assert response.status_code == 404
