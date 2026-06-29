import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';

const BACKEND_URL = process.env.CHATBOT_BACKEND_URL || 'http://localhost:8000';

/**
 * POST /api/chatbot — Proxy chat messages to the FastAPI backend.
 *
 * Accepts JSON body: { message, session_id?, history? }
 * Returns the AI response with task classification metadata.
 */
export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    const body = await request.json();

    const response = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: body.message || '',
        session_id: body.session_id || null,
        user_id: user?.id || null,
        history: body.history || [],
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        {
          response: 'Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn. Vui lòng thử lại.',
          task_type: 'error',
          session_id: body.session_id || '',
          metadata: { error: errorText },
        },
        { status: 200 } // Return 200 to the frontend, error is in the response
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Chatbot proxy error:', error);

    // Check if it's a connection error (backend not running)
    const isConnectionError =
      error instanceof TypeError && (error as any).cause?.code === 'ECONNREFUSED';

    const errorMessage = isConnectionError
      ? '**Chatbot backend chưa khởi động.**\n\nVui lòng chạy:\n```\ncd backend/chatbot\nuvicorn server:app --port 8000\n```'
      : 'Đã xảy ra lỗi kết nối. Vui lòng thử lại.';

    return NextResponse.json(
      {
        response: errorMessage,
        task_type: 'error',
        session_id: '',
        metadata: {},
      },
      { status: 200 }
    );
  }
}
