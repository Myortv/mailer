import datetime

from typing import Optional, Any

from pydantic import BaseModel
from pydantic import validator

from scheduler.schemas.client import ClientFliter


class MailingBase(BaseModel):
    start_time: datetime.datetime
    end_time: datetime.datetime
    body: str
    filters: dict | Any = dict()

    # @validator('start_time', 'end_time')
    # def is_time_valid(cls, v):
    #     if v:
    #         if v >= datetime.datetime.now():
    #          return v
    #     else:
    #          raise ValueError(f'time ({v}) is too small!')

    def return_filter(self):
        filter = ClientFliter(**self.filters)
        return filter

class MailingInDB(MailingBase):
    id: int


class MailingUpdate(MailingBase):
    pass
