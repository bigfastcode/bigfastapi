from pydantic import BaseModel
from typing import Optional, List


class HashableBaseModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class SMS(HashableBaseModel):
    sender: str
    recipient: list
    content: str
    message_type: str = "sms"