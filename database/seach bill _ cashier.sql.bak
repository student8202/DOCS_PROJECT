-- search folio bill in house
spSearchFolioTransaction 0, 0, 0, 1, 0, 0, 0, '', '', '', '', '', '', '', '', '', '', '', '', '02/05/2026', 0, 0, '', 0, '';
-- currency folionum
SELECT C.NoOfDec
FROM Folio F
     JOIN CurrencyDef C ON F.FolioCurrencyCode = C.CurrencyCode
WHERE F.FolioNum = 10123;
-- information folio and guest
SELECT F.FolioExRate, F.FolioNum, F.FolioSubNum, F.ConfirmNum, A.FirstName, A.LastName, RoomCode, A.ArrivalTime, A.DepartureTime, AdtStatus, CreditCardNum,
    CreditCardExpireTime, RateAmount, FolioCurrencyCode, Notice, F.TravelAgent1Code, F.ARAccountNumber, COALESCE(NoPostFlag, 0) AS NoPost
FROM Folio F
     JOIN AdditionalName A ON F.FolioNum = A.FolioNum
WHERE A.FolioNum = 10123 AND IdAddition = 103;
-- F.TravelAgent1Code thông tin Company
SELECT ClientName FROM CLIENT WHERE ClientFolioNum = 4629;
-- service charge
SELECT SvcCode FROM Folio_Svc WHERE FolioNum = 10123;
-- proc có bao nhiêu tab ngoại trừ P, V
EXEC CHGetFolioBalanceCode '10123', 0;

-- proc show all bal: tất cả tab
EXEC CHGetFolioBalanceCode '10123', 1;
-- max transaction id lúc bắt đầu xem
SELECT MAX(TransactionID) AS D
FROM FolioTransaction
WHERE FolioNum = 10123;
-- xem balance của folionum
EXEC GetBalance '10123';
-- xem chi tiết giao dịch của folionum 10123, tab A
EXEC CHGetFolioTransactionNew '10123', 'A ', 1;
-- có được max transactionID nếu có số lớn hơn hiểu là có thêm giao dịch mới
SELECT TOP 1 TransactionID
FROM FolioTransaction
WHERE FolioNum = 10123 AND TransactionID > 668;

