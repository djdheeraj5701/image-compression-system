from enum import Enum

from pydantic import BaseModel


class StatusEnum(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class StatusDTO(BaseModel):
    request_id: str
    status: str
