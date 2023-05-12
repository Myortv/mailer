from pydantic import ValidationError
from fastapi import HTTPException

import logging


def resolve_detail_conflict(e):
    try:
        detail = e.detail
    except:
        detail = e.__str__()
    finally:
        return detail


def raise_exception(e):
    try:
        status_code = e.status_code
    except:
        status_code = 500

    detail = resolve_detail_conflict(e)
    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )

# async def raise_exceptions(func):
#     async def wrapper(*args, **kwargs):
#         try:
#             return await func(*args, **kwargs)
#         except ValidationError as e:
#             raise_exception(e)
#         except HTTPException as e:
#             raise_exception(e)
#         except Exception as e:
#             logging.warning(e)
#             raise e
