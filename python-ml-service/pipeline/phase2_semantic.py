import json
import os
import re
from google import genai
from google.genai import types
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm
from dotenv import load_dotenv

# Load env variables for Gemini API Key
load_dotenv(dotenv_path='../.env.local')

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
gemini_client = None
if api_key:
    gemini_client = genai.Client(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in .env.local")

# Define 14 core roles taxonomy
CORE_ROLES = [
    "Frontend Developer", "Backend Developer", "Fullstack Developer",
    "Mobile Developer", "DevOps Engineer", "Data Engineer",
    "Data Scientist", "Machine Learning Engineer", "QA/Tester",
    "UI/UX Designer", "Product Manager", "Project Manager",
    "Business Analyst", "System Administrator"
]

class SemanticNormalizer:
    def __init__(self):
        print("Initializing SemanticNormalizer and loading BAAI/bge-m3...")
        self.model = SentenceTransformer('BAAI/bge-m3')
        self.core_embeddings = self.model.encode(CORE_ROLES)
        
    def get_cosine_similarity(self, vec1, vec2):
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    def normalize_title(self, raw_title: str) -> str:
        # Strip simple noise
        clean_title = re.sub(r'(Tuyển gấp|Lương Thưởng Hấp Dẫn|Thu nhập|Lên tới|Upto).*', '', raw_title, flags=re.IGNORECASE)
        clean_title = clean_title.strip()
        
        # 1. Embed and check similarity
        title_embedding = self.model.encode([clean_title])[0]
        
        best_score = -1
        best_role = ""
        
        for i, core_embedding in enumerate(self.core_embeddings):
            score = self.get_cosine_similarity(title_embedding, core_embedding)
            if score > best_score:
                best_score = score
                best_role = CORE_ROLES[i]
                
        # 2. Fast Path: If similarity > 0.85, map instantly
        if best_score > 0.85:
            return best_role
            
        # 3. Fallback: Call Gemini if confidence is low
        return self._fallback_llm_title(clean_title)

    def _fallback_llm_title(self, title: str) -> str:
        if not gemini_client:
            return title
            
        prompt = f"""
        Phân loại chức danh công việc sau đây vào 1 trong 14 nhóm sau:
        {CORE_ROLES}
        Nếu không khớp nhóm nào, hãy trả về 'Other'.
        Chỉ trả về TÊN NHÓM, KHÔNG giải thích.
        
        Chức danh: "{title}"
        """
        
        try:
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                )
            )
            
            result = response.text.strip()
            for role in CORE_ROLES:
                if role.lower() in result.lower():
                    return role
        except Exception as e:
            print(f"Gemini Title Fallback error: {e}")
            
        return title # Return original if LLM fails

    def extract_skills_json(self, job_description: str) -> List[str]:
        if not gemini_client:
            return []
            
        prompt = f"""
        Extract all technical tools, programming languages, and frameworks from the following job description.
        Return the result STRICTLY as a JSON string array. Do NOT output any other text or markdown.
        Example output: ["Java", "Spring Boot", "MySQL"]
        
        Job Description:
        {job_description[:2000]} # Limit to avoid context window explosion
        """
        
        try:
            # We enforce JSON output using generation_config
            response = gemini_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                )
            )
            
            result = response.text.strip()
            try:
                skills = json.loads(result)
                if isinstance(skills, list):
                    return skills
            except json.JSONDecodeError:
                print(f"Failed to parse Gemini JSON output: {result}")
        except Exception as e:
            print(f"Gemini Skills Extraction error: {e}")
            
        return []

# Singleton instance
_normalizer = None
def get_semantic_normalizer():
    global _normalizer
    if _normalizer is None:
        _normalizer = SemanticNormalizer()
    return _normalizer
