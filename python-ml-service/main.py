from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import json

from pipeline.phase1_clean import clean_company_name, clean_location
from pipeline.phase2_semantic import get_semantic_normalizer
from pipeline.phase3_hash import generate_job_hash
from pipeline.phase4_upsert import upsert_job

app = FastAPI(title="Job Market ML Pipeline", version="1.0.0")

class RawJobInput(BaseModel):
    url: str
    tieu_de: str
    cong_ty: str
    dia_diem: str
    mo_ta_cong_viec: Optional[str] = ""
    # Add other fields as needed
    muc_luong: Optional[str] = "Thỏa thuận"
    logo: Optional[str] = ""
    hinh_thuc_lam_viec: Optional[str] = "Toàn thời gian"

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/jobs/process")
def process_job(job: RawJobInput):
    """
    Nhận dữ liệu thô từ Playwright scraper, chạy qua 4 Phase chuẩn hóa và lưu vào Database.
    """
    try:
        # Phase 1: Clean Mandatory Fields
        norm_company = clean_company_name(job.cong_ty)
        norm_location = clean_location(job.dia_diem)
        
        # Phase 2: Semantic Normalization (Title & Skills)
        normalizer = get_semantic_normalizer()
        norm_title = normalizer.normalize_title(job.tieu_de)
        
        skills = []
        if job.mo_ta_cong_viec and job.mo_ta_cong_viec != "N/A":
            skills = normalizer.extract_skills_json(job.mo_ta_cong_viec)
            
        # Convert skills list to JSONB compatible string if needed, or keep as list 
        # depending on Supabase column type (jsonb or text[])
        
        # Phase 3: Hashing Engine
        job_hash = generate_job_hash(norm_company, norm_title, norm_location)
        
        # Construct the final normalized object
        normalized_job_data = {
            "job_hash_id": job_hash,
            "url": job.url,
            "tieu_de_goc": job.tieu_de,
            "tieu_de_chuan_hoa": norm_title,
            "cong_ty_goc": job.cong_ty,
            "cong_ty_chuan_hoa": norm_company,
            "dia_diem_goc": job.dia_diem,
            "dia_diem_chuan_hoa": norm_location,
            "ky_nang": skills, # Assumes jsonb column
            "muc_luong": job.muc_luong,
            "logo": job.logo,
            "hinh_thuc_lam_viec": job.hinh_thuc_lam_viec,
            "mo_ta_cong_viec": job.mo_ta_cong_viec
        }
        
        # Phase 4: Efficient Upsert
        result = upsert_job(normalized_job_data)
        
        if result["success"]:
            return {
                "message": "Job processed and saved successfully.",
                "job_hash": job_hash,
                "normalized_data": normalized_job_data
            }
        else:
            raise HTTPException(status_code=500, detail=f"Database Upsert failed: {result.get('error')}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
