import hashlib
import re
from datetime import datetime

def generate_job_hash(company_name: str, job_title: str, location: str) -> str:
    """
    Tạo mã định danh duy nhất (Hash ID) dựa trên 3 yếu tố cốt lõi.
    Cơ chế này giúp nhận diện bài đăng trùng lặp từ nhiều trang tuyển dụng khác nhau.
    """
    # Chuẩn hóa chuỗi trước khi băm (viết thường, bỏ khoảng trắng thừa)
    company = re.sub(r'\s+', ' ', str(company_name)).strip().lower()
    title = re.sub(r'\s+', ' ', str(job_title)).strip().lower()
    loc = location.strip().lower()
    
    unique_string = f"{company}|{title}|{loc}"
    
    # Lấy YYYY-MM
    current_month = datetime.now().strftime("%Y-%m")
    unique_string += f"|{current_month}"
        
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
