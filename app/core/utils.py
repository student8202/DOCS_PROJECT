def tcvn3_to_unicode(tcvn3_str):
    if not tcvn3_str or not isinstance(tcvn3_str, str):
        return tcvn3_str

    # Bảng mã ASCII TCVN3 chuẩn từ SQL của bạn
    tcvn_codes = [
        184, 181, 182, 183, 185, 168, 190, 187, 188, 189, 198, 169, 202, 199, 200, 201, 203, 208, 204, 206, 
        207, 209, 170, 213, 210, 211, 212, 214, 221, 215, 216, 220, 222, 227, 223, 225, 226, 228, 171, 232, 
        229, 230, 231, 233, 172, 237, 234, 235, 236, 238, 243, 239, 241, 242, 244, 173, 248, 245, 246, 247, 
        249, 253, 250, 251, 252, 254, 174, 
        # Phần mã cho chữ HOA (Thường nằm ở dải 161-167)
        161, 162, 163, 164, 165, 166, 167
    ]
    
    # Bảng mã Unicode tương ứng
    unicode_codes = [
        225, 224, 7843, 227, 7841, 259, 7855, 7857, 7859, 7861, 7863, 226, 7845, 7847, 7849, 7851, 7853, 233, 232, 7867, 
        7869, 7865, 234, 7871, 7873, 7875, 7877, 7879, 237, 236, 7881, 297, 7883, 243, 242, 7887, 245, 7885, 244, 7889, 
        7891, 7893, 7895, 7897, 417, 7899, 7901, 7903, 7905, 7907, 250, 249, 7911, 361, 7909, 432, 7913, 7915, 7917, 7919, 
        7921, 253, 7923, 7927, 7929, 7925, 273, 
        # Chữ HOA tương ứng: Ă, Â, Ê, Ô, Ơ, Ư, Đ
        258, 194, 202, 212, 416, 431, 272 
    ]

    mapping = dict(zip(tcvn_codes, unicode_codes))

    # Bổ sung các mã điều khiển (1-31) thường dùng cho dấu Chữ Hoa trong TCVN3
    extra_map = {
        1: 224, 2: 7842, 3: 195, 4: 193, 5: 7840, # À, Ả, Ã, Á, Ạ
        6: 232, 7: 7866, 8: 7868, 9: 201, 10: 7864, # È, Ẻ, Ẽ, É, Ẹ
        11: 236, 12: 7880, 13: 296, 14: 205, 15: 7882 # Ì, Ỉ, Ĩ, Í, Ị
    }
    mapping.update(extra_map)

    res = []
    for char in tcvn3_str:
        ascii_val = ord(char)
        if ascii_val in mapping:
            res.append(chr(mapping[ascii_val]))
        else:
            res.append(char)
            
    # Chuyển về kiểu Proper Case (Nguyễn Trần Tuấn Vũ) cho đẹp nếu cần
    # return "".join(res).title().strip() 
    return "".join(res).strip()
