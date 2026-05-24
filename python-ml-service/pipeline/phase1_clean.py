import re
from unidecode import unidecode

def clean_company_name(raw_name: str) -> str:
    if not raw_name:
        return "Unknown"
    
    # Chuyển về chữ thường
    name = raw_name.lower().strip()
    
    # Loại bỏ các tiền tố/hậu tố pháp nhân
    legal_entities = [
        "công ty cổ phần", "cong ty co phan", "ctcp", "công ty cp", "cong ty cp", "cp",
        "công ty tnhh", "cong ty tnhh", "tnhh",
        "công ty mtv", "cong ty mtv", "mtv",
        "tập đoàn", "tap doan",
        "jsc", "jsc.", "joint stock company",
        "co., ltd", "coltd", "co. ltd", "co.,ltd", "ltd", "ltd.", "company limited",
        "công ty", "cong ty", "cty"
    ]
    
    # Thay thế các từ này bằng chuỗi rỗng
    for entity in legal_entities:
        # Dùng regex \b để match chính xác từ thay vì chuỗi con
        pattern = r'\b' + re.escape(entity) + r'\b'
        name = re.sub(pattern, '', name)
    
    # Bỏ các dấu câu, ký tự đặc biệt thừa
    name = re.sub(r'[\-\(\)\[\]\.\,]', ' ', name)
    
    # Xóa khoảng trắng thừa và unidecode (chuyển sang tiếng Việt không dấu)
    name = re.sub(r'\s+', ' ', name).strip()
    return unidecode(name)

def clean_location(raw_location: str) -> str:
    if not raw_location:
        return "N/A"
        
    loc = raw_location.lower().strip()
    
    # Từ điển ánh xạ location
    HCM_ALIASES = ["hcm", "sài gòn", "tp. hồ chí minh", "thành phố hồ chí minh", "ho chi minh", "tp hcm"]
    HN_ALIASES = ["hà nội", "ha noi", "thủ đô hà nội", "hn"]
    DN_ALIASES = ["đà nẵng", "da nang", "tp đà nẵng", "dn"]
    
    if any(alias in loc for alias in HCM_ALIASES):
        return "Ho Chi Minh"
    elif any(alias in loc for alias in HN_ALIASES):
        return "Ha Noi"
    elif any(alias in loc for alias in DN_ALIASES):
        return "Da Nang"
    
    return unidecode(loc).title()
