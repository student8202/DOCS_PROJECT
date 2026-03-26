from pydantic import BaseModel
from typing import Optional

class DeviceRegisterSchema(BaseModel):
    DeviceID: str
    ConnectionID: str
    ModuleName: str
    DeviceType: Optional[str] = "TABLET"

class DevicePingSchema(BaseModel):
    DeviceID: str
    ConnectionID: str
