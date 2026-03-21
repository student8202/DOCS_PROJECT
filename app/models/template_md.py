from datetime import datetime
from typing import Optional

class TemplateModel:
    def __init__(
        self,
        TemplateID: Optional[int] = None,
        TemplateCode: str = "",
        TemplateName: str = "",
        ModuleName: str = "",   # FO, POS, BO, HR
        SubModule: str = "",    # RESERVATION, CASHIER, OUTLET...
        Category: str = "",     # REG_CARD, INVOICE...
        IsCustom: int = 1,      # 1: CKEditor, 0: Dev
        HtmlContent: Optional[str] = None,
        FilePath: Optional[str] = None,
        IsActive: bool = True,
        CreatedBy: str = "",
        CreatedAt: datetime = None
    ):
        self.TemplateID = TemplateID
        self.TemplateCode = TemplateCode
        self.TemplateName = TemplateName
        self.ModuleName = ModuleName
        self.SubModule = SubModule
        self.Category = Category
        self.IsCustom = IsCustom
        self.HtmlContent = HtmlContent
        self.FilePath = FilePath
        self.IsActive = IsActive
        self.CreatedBy = CreatedBy
        self.CreatedAt = CreatedAt or datetime.now()
