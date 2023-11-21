import uuid
from pydantic import BaseModel, validator


class BaseProperties(BaseModel):
    @validator("uuid", pre=True, always=True, check_fields=False)
    def default_hashed_id(cls, v):
        return v or uuid.uuid4()


class BaseUserCreate(BaseProperties):
    tg_id: int
    first_name: str

    class Config:
        from_attributes = True


class BaseRouteCreate(BaseProperties):
    start_station: str
    finish_station: str

    class Config:
        from_attributes = True