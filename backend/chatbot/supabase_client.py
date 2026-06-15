"""Supabase Client for Chatbot.

Used to read/write persistent resume data from the `user_resume_data` table.
"""

import logging
import os
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Try to load from .env.local if not in env
# The chatbot might be running from /backend/chatbot or docker root
try:
    from dotenv import load_dotenv
    # Find .env.local in repo root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))
    env_path = os.path.join(repo_root, ".env.local")
    if os.path.exists(env_path):
        load_dotenv(env_path)
except ImportError:
    pass

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

class SupabaseClient:
    def __init__(self):
        self._client: Client | None = None

    def connect(self):
        if self._client is None and SUPABASE_URL and SUPABASE_KEY:
            self._client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("SupabaseClient initialized.")
        elif self._client is None:
            logger.warning("Supabase credentials missing. SupabaseClient will fail.")

    def upsert_user_resume(self, user_id: str, resume_dict: dict, resume_name: str, quality_score: int, num_experience: int, num_skills: int):
        """Upsert the extracted resume JSON into user_resume_data."""
        if not self._client:
            self.connect()
        if not self._client:
            return None
        
        try:
            data = {
                "user_id": user_id,
                "resume_json": resume_dict,
                "quality_score": quality_score,
                "num_experience": num_experience,
                "num_skills": num_skills,
                "source_file_name": resume_name,
            }
            res = self._client.table("user_resume_data").upsert(data).execute()
            return res.data
        except Exception as e:
            logger.error(f"Failed to upsert resume to Supabase for user {user_id}: {e}")
            return None

    def get_user_resume(self, user_id: str) -> tuple[str | None, dict | None]:
        """Fetch persistent resume from Supabase."""
        if not self._client:
            self.connect()
        if not self._client:
            return None, None
            
        try:
            res = self._client.table("user_resume_data").select("*").eq("user_id", user_id).execute()
            if res.data and len(res.data) > 0:
                record = res.data[0]
                return record.get("source_file_name"), record.get("resume_json")
            return None, None
        except Exception as e:
            logger.error(f"Failed to get user resume from Supabase for user {user_id}: {e}")
            return None, None

supabase_client = SupabaseClient()
