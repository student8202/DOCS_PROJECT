from datetime import datetime 

class SignedDocumentModel:
    # Tên bảng thực tế trong Database
    TABLE_NAME = "dbo.tbl_SignedDocuments" 

    # Câu lệnh INSERT chuẩn (Dùng cho pyodbc)
    SQL_INSERT = f"""
        INSERT INTO {TABLE_NAME} (
            Doc_GUID, Doc_Group_ID, Booking_ID, Folio_Num, Group_Code, IdAddition,
            Doc_Type, Source_Type, Owner_Dept, Guest_Name_SS, 
            Data_JSON_Full_SS, FilePath, Signature_Base64, File_Extension, 
            Status, CreatedBy, CreatedAt, IsDeleted, IsCurrent
        ) VALUES (NEWID(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2, ?, GETDATE(), 0, 1)
    """
    SQL_INSERT_NEW = """
        INSERT INTO dbo.tbl_SignedDocuments 
        (Doc_GUID, Booking_ID, Folio_Num, Group_Code, IdAddition, 
         Doc_Type, Source_Type, Owner_Dept, Guest_Name_SS, Data_JSON_Full_SS, 
         FilePath, Signature_Base64, File_Extension, Status, Version, 
         IsCurrent, CreatedBy, CreatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 3, ?, 1, ?, GETDATE())
    """
