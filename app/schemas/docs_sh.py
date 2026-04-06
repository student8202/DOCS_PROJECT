from pydantic import BaseModel
from typing import Optional

class ApproveSchema(BaseModel):
    # ID của hồ sơ trong hàng đợi (Bắt buộc)
    QueueID: int 
    
    # Ghi chú của Lễ tân khi duyệt (Nếu có)
    Notes: Optional[str] = None 
    
    # Loại hồ sơ: REG_CARD hoặc CONFIRM (Để kiểm tra chéo)
    DocType: str
