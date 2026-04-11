from pydantic import BaseModel
from typing import Optional

class FolioSearchRequest(BaseModel):
    noShow: int = 0
    reserved: int = 0
    canceled: int = 0
    inHouse: int = 1
    arrivalToday: int = 0
    checkOutToday: int = 0
    checkOut: int = 0
    sNumInfo: Optional[str] = ""
    name: Optional[str] = ""
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    companyID: Optional[str] = ""
    groupID: Optional[str] = ""
    countryID: Optional[str] = ""
    roomCode: Optional[str] = ""
    arrivalDateFrom: Optional[str] = ""
    arrivalDateTo: Optional[str] = ""
    departureDateFrom: Optional[str] = ""
    departureDateTo: Optional[str] = ""
    hotelDate: str
    exactly: int = 0
    includePf: int = 0
    sTAorARNum: Optional[str] = ""
    isNotBalance: int = 0
    cruiseCode: Optional[str] = ""