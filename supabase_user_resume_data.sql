-- Supabase Migration: Create user_resume_data table

CREATE TABLE IF NOT EXISTS public.user_resume_data (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  resume_json JSONB NOT NULL,
  quality_score INTEGER DEFAULT 0,
  num_experience INTEGER DEFAULT 0,
  num_skills INTEGER DEFAULT 0,
  source_file_name TEXT,
  extracted_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.user_resume_data ENABLE ROW LEVEL SECURITY;

-- Users can read their own resume data
CREATE POLICY "Users can view own resume data" ON public.user_resume_data
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can update their own resume data (via frontend/API if needed, though backend uses service role)
CREATE POLICY "Users can insert own resume data" ON public.user_resume_data
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own resume data" ON public.user_resume_data
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own resume data" ON public.user_resume_data
  FOR DELETE
  USING (auth.uid() = user_id);
