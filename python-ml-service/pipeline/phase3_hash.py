import hashlib
from datetime import datetime

def generate_job_hash(company_name: str, title: str, location: str, include_month_year: bool = True) -> str:
    """
    Tạo mã băm duy nhất (SHA-256) dựa trên 3 trường bắt buộc.
    Nếu include_month_year = True, sẽ thêm tháng/năm hiện tại vào hash để
    cho phép 1 công ty tuyển lại cùng 1 vị trí ở cùng 1 địa điểm sau vài tháng.
    """
    
    # Đảm bảo dữ liệu đầu vào sạch sẽ trước khi hash
    comp = company_name.strip().lower()
    tit = title.strip().lower()
    loc = location.strip().lower()
    
    unique_string = f"{comp}|{tit}|{loc}"
    
    if include_month_year:
        # Lấy YYYY-MM
        current_month = datetime.now().strftime("%Y-%m")
        unique_string += f"|{current_month}"
        
    return hashlib.sha256(unique_string.encode('utf-8')).hexdigest()
