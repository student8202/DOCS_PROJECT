from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
import uuid
import datetime
from .template_md import Base

class SignedDocumentModel(Base):
    __tablename__ = 'tbl_SignedDocuments'
    __table_args__ = {"schema": "FO"}

    Doc_GUID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    Booking_ID = Column(String(50), index=True)
    Group_Code = Column(String(50), index=True, nullable=True)
    Folio_Num = Column(String(50), nullable=True)
    Doc_Type = Column(String(50)) # VD: CONFIRM, REGCARD
    
    # Dữ liệu Snapshot (Kết quả trả về từ Procedure của bạn)
    Guest_Name_SS = Column(String(255))
    Total_Amount_SS = Column(Numeric(18, 2))
    Data_JSON_Full_SS = Column(Text) # Lưu toàn bộ JSON kết quả của Proc
    
    # Thông tin chữ ký và file
    FilePath = Column(String(500)) # Đường dẫn file PDF sau khi xuất
    Signature_Base64 = Column(Text) # Chuỗi Base64 chữ ký khách vẽ
    
    Status = Column(Integer, default=1) # 1:Signed, 2:Reject, 3:Void
    Version = Column(Integer, default=1)
    IsDeleted = Column(Boolean, default=False)
    
    CreatedBy = Column(String(50))
    CreatedAt = Column(DateTime, default=datetime.datetime.now)
