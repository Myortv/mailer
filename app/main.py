from app.core.configs import settings

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from app.db.base import DatabaseManager

from fastapi_auth0 import Auth0, Auth0User

from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f'{settings.API_V1_STR}/openapi.json',
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


auth = Auth0(
    settings.OAUTHDOMAIN,
    settings.OAUTHAUDIENCE,
)

settings.AUTH = auth


from app.api.v1 import client, mailing


app.include_router(
    client.router,
    prefix=settings.API_V1_STR,
)
app.include_router(
    mailing.router,
    prefix=settings.API_V1_STR,
)


instrumentator = Instrumentator().instrument(app)


@app.on_event('startup')
async def startup():
    await DatabaseManager.start(
        settings.POSTGRES_DB,
        settings.POSTGRES_USER,
        settings.POSTGRES_PASSWORD,
        settings.POSTGRES_HOST,
    )
    instrumentator.expose(app, include_in_schema=True, should_gzip=True)


@app.on_event('shutdown')
async def shutdown():
    await DatabaseManager.stop()
