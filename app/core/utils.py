def tcvn3_to_unicode(tcvn3_str):
    if not tcvn3_str or not isinstance(tcvn3_str, str):
        return tcvn3_str
        
    # Bảng mã dấu TCVN3 (Chỉ lấy các mã từ 1 đến 5 và 11 đến 25, 30, 31)
    # LOẠI BỎ mã 13 (\r) và 10 (\n) khỏi bảng tra cứu này
    char_map = {
        '\x01': 'à', '\x02': 'ả', '\x03': 'ã', '\x04': 'á', '\x05': 'ạ',
        '\x06': 'è', '\x07': 'ẻ', '\x08': 'ẽ', 
        # '\x09': 'é',  # Mã 9 là phím TAB -> Không dịch
        # '\x0a': 'ẹ',  # Mã 10 là \n (Line Feed) -> Không dịch để giữ xuống dòng
        '\x0b': 'ì', '\x0c': 'ỉ', '\x0d': 'ĩ', '\x0e': 'í', '\x0f': 'ị',
        # '\x0d' thực chất là \r (Carriage Return), 
        # Nếu SMILE dùng \r\n làm xuống dòng thì nên bỏ cả \x0d
        '\x10': 'ò', '\x11': 'ỏ', '\x12': 'õ', '\x13': 'ó', '\x14': 'ọ',
        '\x15': 'ù', '\x16': 'ủ', '\x17': 'ũ', '\x18': 'ú', '\x19': 'ỵ',
        '\x1a': 'đ', '\x1b': 'â', '\x1c': 'ê', '\x1d': 'ô', '\x1e': 'ơ', '\x1f': 'ư'
    }
    
    # Danh sách các ký tự điều khiển TUYỆT ĐỐI GIỮ NGUYÊN
    system_chars = ['\r', '\n', '\t']

    res = ""
    for char in tcvn3_str:
        if char in system_chars:
            res += char # Giữ nguyên để trình duyệt tự xuống dòng
        elif char in char_map:
            res += char_map[char]
        else:
            res += char
            
    return res.strip()
