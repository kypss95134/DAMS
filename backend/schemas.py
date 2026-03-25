from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# Device History Schemas
class DeviceHistoryBase(BaseModel):
    action: str
    assignee: Optional[str] = None
    notes: Optional[str] = None

class DeviceHistoryCreate(DeviceHistoryBase):
    pass

class DeviceHistorySchema(DeviceHistoryBase):
    id: int
    device_id: int
    action_date: datetime

    class Config:
        orm_mode = True

# Device Schemas
class DeviceBase(BaseModel):
    asset_tag: str
    name: str
    department: Optional[str] = None
    assignee: Optional[str] = None
    checkout_date: Optional[date] = None
    return_date: Optional[date] = None
    system_model: Optional[str] = None
    office_number: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "Available"

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    pass

class DeviceSchema(DeviceBase):
    id: int

    class Config:
        orm_mode = True

# Extended Response
class DeviceWithHistorySchema(DeviceSchema):
    history_records: List[DeviceHistorySchema] = []

    class Config:
        orm_mode = True
