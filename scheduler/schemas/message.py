import datetime

from typing import Optional

from pydantic import BaseModel
from pydantic import validator

import re


phonenumber_pattern = re.compile('^7[0-9]{10}$')


class MessageBase(BaseModel):
    mailing_id: int
    client_id: int
    creation_time: Optional[datetime.datetime]
    status: Optional[str] = 'await'

    @validator('mailing_id', 'client_id')
    def is_positive(cls, v):
        if v > 0:
            return v
        else:
            raise ValueError(
                    f'Foreign key value ({v}) should be positive int'
            )

    # @validator('start_time', 'end_time')
    # def is_time_valid(cls, v):
    #       if v:
    #               if v >= datetime.datetime.now():
    #                       return v
    #               else:
    #                       raise ValueError(f'time ({v}) is too small!')


class MessageInDB(MessageBase):
    id: int


class MessageOutPut(BaseModel):
    id: int
    phone: str
    text: str

    @validator('phone')
    def phone_number_correct(cls, v):
        if phonenumber_pattern.match(v):
            return v
        else:
            raise ValueError(f'phone number ({v}) is invalid')


class MessageCreate(MessageBase):
      pass


class MessageRequest(BaseModel):
    id: int
    phone: int
    text: str


class MessageResponse(BaseModel):
    code: int
    message: str
