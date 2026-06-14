import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';

const BACKEND_URL = process.env.CHATBOT_BACKEND_URL || 'http://localhost:8000';

interface RouteParams {
  params: Promise<{ sessionId: string }>;
}

// ─────────────────────────────────────────────────────────────
// GET /api/v1/chat/session/[sessionId]
// Fetch resume info from FastAPI session, with Supabase auth.
// ─────────────────────────────────────────────────────────────
export async function GET(_request: NextRequest, { params }: RouteParams) {
  try {
    const { sessionId } = await params;
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const res = await fetch(`${BACKEND_URL}/api/history/${sessionId}`);
    if (!res.ok) {
      return NextResponse.json({ error: 'Session not found' }, { status: 404 });
    }

    const data = await res.json();

    // Only return resume metadata, not full history
    return NextResponse.json({
      resume_id: data.resume_id || null,
      resume_name: data.resume_name || null,
    });
  } catch (err) {
    console.error('[GET /session/[sessionId]]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
