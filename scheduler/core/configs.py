from typing import Any, Dict, List, Optional

from fastapi_auth0 import Auth0

from pydantic import BaseSettings, AnyUrl, validator

from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    MAILING_SERVER_URL: AnyUrl
    AUTHTOKEN: str

    SCHEDULER: AsyncIOScheduler = None
    LOGGING_FILE: str

settings = Settings()
