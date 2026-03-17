from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class InHouseRead(BaseModel):
    AdtStatus: Optional[int] = 0
    FolioNum: Optional[int] = 0
    ConfirmNum: Optional[int] = 0
    Title: Optional[str] = ""
    LastName: Optional[str] = ""
    FirstName: Optional[str] = "" # Giá/RateCode
    RoomCode: Optional[str] = ""
    RoomTypeCode: Optional[str] = ""
    ArrivalDate: Optional[datetime] = None
    DepartureDate: Optional[datetime] = None
    NumGuest: Optional[str] = ""
    CompanyName: Optional[str] = ""
    CompFlag: Optional[int] = 0
    HUFlag: Optional[int] = 0
    TimeArrival: Optional[datetime] = None
    TimeDeparture: Optional[datetime] = None
    BookTime: Optional[datetime] = None
    NumAdt: Optional[int] = 0
    NumChild: Optional[int] = 0
    NumEnf: Optional[int] = 0
    SpecialService: Optional[str] = ""
    Notice: Optional[str] = ""

    class Config:
        from_attributes = True
