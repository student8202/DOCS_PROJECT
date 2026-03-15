class FOModel:
    # 1. SQL lấy ngày khách sạn hiện tại từ SMILE
    SQL_GET_HOTEL_DATE = "SELECT TOP 1 HotelDate FROM SMILE_FO.dbo.Hotelparameter"

    # 2. SQL gọi SP In-house (41 tham số, HotelDate nằm ở vị trí số 20)
    # @InHouse=1 (tham số thứ 4)
    SQL_GET_INHOUSE_GUESTS = "{call SMILE_FO.dbo.spSearchFolioFlexible(0,0,0,1,0,0,0,'0','','','','','','','','','','','',?,0,0,'','',0,1,1,1,NULL,'','','','','','','','','','','','')}"