from pydantic import BaseModel

class PlaybookCreate(BaseModel):
    playbook_id:str

class VersionCreate(BaseModel):
    content:str

class VersionResponse(BaseModel):
    version :int
    content:str
    createdAt:str


class CapacityInfo(BaseModel):
    RCU: float | None = None
    WCU: float | None = None


class VersionResponseWithCapacity(BaseModel):
    data: VersionResponse
    consumed_capacity: CapacityInfo