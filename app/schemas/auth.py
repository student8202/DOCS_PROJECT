from pydantic import BaseModel
from typing import Optional, List
from base import BaseAuditSchema

class UserOut(BaseAuditSchema):
    Username: str
    FullName: Optional[str]
    Source_Map: Optional[str]
    IsActive: bool
    Department: Optional[str]
