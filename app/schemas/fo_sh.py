from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class InHouseRead(BaseModel):
    RoomCode: Optional[str] = None
    LastName: Optional[str] = None
    FirstName: Optional[str] = None
    ArrivalDate: Optional[datetime] = None
    DepartureDate: Optional[datetime] = None
    CompanyName: Optional[str] = None
    NumGuest: Optional[str] = None # Vd: 2/1/0 (Adt/Chd/Enf)
