from pydantic import BaseModel, Field
from typing import Optional

class DepartmentSaveRequest(BaseModel):
    DeptID: Optional[int] = None
    DeptName: str = Field(..., min_length=1)