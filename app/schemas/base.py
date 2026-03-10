from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseAuditSchema(BaseModel):
    CreatedBy: Optional[str] = None
    CreatedAt: Optional[datetime] = None
    UpdatedBy: Optional[str] = None
    UpdatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True
