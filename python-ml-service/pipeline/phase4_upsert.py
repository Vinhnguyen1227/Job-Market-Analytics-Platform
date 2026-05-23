from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv(dotenv_path='../.env.local')

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use service role key to bypass RLS

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Missing Supabase credentials in environment variables.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upsert_job(job_data: dict) -> dict:
    """
    Sử dụng PostgreSQL Upsert thông qua Supabase.
    job_data phải chứa khóa chính (hoặc unique constraint) là 'job_hash_id'.
    """
    supabase = get_supabase_client()
    
    if 'job_hash_id' not in job_data:
        raise ValueError("job_data must contain 'job_hash_id' for upserting.")
        
    try:
        # Perform upsert
        # Note: In supabase-py, upsert automatically uses the Primary Key to resolve conflicts.
        # If job_hash_id is a UNIQUE constraint but not PK, you might need to specify on_conflict.
        # supabase-py v2 allows passing on_conflict
        # Perform upsert using URL as the unique identifier to avoid duplicate URL errors
        response = (
            supabase.table('jobs')
            .upsert(job_data, on_conflict='url')
            .execute()
        )
        return {"success": True, "data": response.data}
    except Exception as e:
        print(f"Error upserting job: {e}")
        return {"success": False, "error": str(e)}
