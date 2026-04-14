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
--------------------------------- Detail bill
SELECT TOP 1 TransactionID
FROM FolioTransaction
WHERE FolioNum = 10123 AND TransactionID > 722;

SELECT TransactionID, F.TransactionSubCode, T.Description, TransactionAmount * 1 AS Amount, F.SystemTime
FROM FolioTransaction F
     LEFT JOIN TransactionCode T ON F.TransactionCode = T.TransactionCode AND F.TransactionSubCode = T.TransactionSubCode
WHERE FolioNum = 10123 AND F.TransactionCode = '140' AND RefNumber = '1012301' AND FolioBalanceCode = 'B ' AND TransactionDate = '02/05/2026'
      AND DATEPART(yyyy, SystemTime) = DATEPART(yyyy, '04/14/2026 20:28:03') AND DATEPART(mm, SystemTime) = DATEPART(mm, '04/14/2026 20:28:03')
      AND DATEPART(dd, SystemTime) = DATEPART(dd, '04/14/2026 20:28:03') AND DATEPART(hh, SystemTime) = DATEPART(hh, '04/14/2026 20:28:03')
      AND DATEPART(mi, SystemTime) = DATEPART(mi, '04/14/2026 20:28:03') AND DATEPART(ss, SystemTime) = DATEPART(ss, '04/14/2026 20:28:03');

SELECT PostedTime AS ndate, PostedClerkID, IName, Qty, Price, NULL AS BaseSub, NULL AS BaseTax, NULL AS BaseSrc, Amount
FROM ItemPosted
WHERE TrnID = 722;

SELECT PostedTime AS ndate, PostedClerkID, IName, Qty, Price, NULL AS BaseSub, NULL AS BaseTax, NULL AS BaseSrc, Amount
FROM ItemPosted
WHERE TrnID = 722;

SELECT TransactionID, F.TransactionSubCode, T.Description, TransactionAmount * 1 AS Amount
FROM FolioTransaction F
     LEFT JOIN TransactionCode T ON F.TransactionCode = T.TransactionCode AND F.TransactionSubCode = T.TransactionSubCode
WHERE FolioNum = 10123 AND F.TransactionCode = '200' AND RefNumber = '100000312' AND FolioBalanceCode = 'B ' AND TransactionDate = '02/05/2026'
      AND DATEPART(yyyy, SystemTime) = DATEPART(yyyy, '04/14/2026 21:27:44') AND DATEPART(mm, SystemTime) = DATEPART(mm, '04/14/2026 21:27:44')
      AND DATEPART(dd, SystemTime) = DATEPART(dd, '04/14/2026 21:27:44') AND DATEPART(hh, SystemTime) = DATEPART(hh, '04/14/2026 21:27:44')
      AND DATEPART(mi, SystemTime) = DATEPART(mi, '04/14/2026 21:27:44') AND DATEPART(ss, SystemTime) = DATEPART(ss, '04/14/2026 21:27:44');

SELECT PostedTime AS ndate, PostedClerkID, IName, Qty, Price, NULL AS BaseSub, NULL AS BaseTax, NULL AS BaseSrc, Amount
FROM ItemPosted
WHERE TrnID = 725;

SELECT * FROM GlobalParameter WHERE ParaName = 'POSDatabase';

SELECT DecDiv FROM SMILE_POS.dbo.CurrencyDef WHERE CrCode = 1;

SELECT CAST(NDay AS VARCHAR(2))+'/'+CAST(NMonth AS VARCHAR(2)) AS ndate, Cashier, TrnDesc, TrnQty, ItemPrice / 1 AS Price, BaseSub / 100 AS BaseSub,
    BaseTax / 1 AS BaseTax, BaseSrc, BaseTTL / 1 AS BaseTotal
FROM SMILE_POS.dbo.Trn
WHERE CheckNo = 100000312; --And TrnCode in (100,110) Order by BaseTotal desc
