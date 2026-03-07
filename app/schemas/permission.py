from pydantic import BaseModel
from typing import List

class SaveViewRightsRequest(BaseModel):
    EmployeeID: int
    DeptIDs: List[int] # Tự động validate dữ liệu là mảng số nguyên