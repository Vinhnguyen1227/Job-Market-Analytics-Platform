import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';

const BACKEND_URL = process.env.CHATBOT_BACKEND_URL || 'http://localhost:8000';

/**
 * POST /api/chatbot/upload — Proxy file uploads to the FastAPI backend.
 *
 * Accepts multipart/form-data with: file, session_id?
 * Runs Phase 2→4 pipeline and returns resume_id + quality metrics.
 */
export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();

    const formData = await request.formData();
    const file = formData.get('file') as File | null;
    const sessionId = formData.get('session_id') as string | null;

    if (!file) {
      return NextResponse.json(
        { success: false, error: 'No file provided', message: 'Vui lòng chọn file để tải lên.' },
        { status: 400 }
      );
    }

    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'image/png',
      'image/jpeg',
    ];

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|doc|png|jpg|jpeg)$/i)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid file type',
          message: 'Chỉ hỗ trợ file PDF, DOCX, hoặc ảnh (PNG/JPG).',
        },
        { status: 400 }
      );
    }

    // Forward to backend
    const backendForm = new FormData();
    backendForm.append('file', file);
    if (sessionId) {
      backendForm.append('session_id', sessionId);
    }
    if (user?.id) {
      backendForm.append('user_id', user.id);
    }

    const response = await fetch(`${BACKEND_URL}/api/upload`, {
      method: 'POST',
      body: backendForm,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Upload backend error: ${response.status} ${errorText}`);
      return NextResponse.json(
        {
          success: false,
          error: errorText,
          message: 'Lỗi xử lý file. Vui lòng thử lại.',
        },
        { status: 200 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Upload proxy error:', error);

    const isConnectionError =
      error instanceof TypeError && (error as any).cause?.code === 'ECONNREFUSED';

    return NextResponse.json(
      {
        success: false,
        error: String(error),
        message: isConnectionError
          ? '**Chatbot backend chưa khởi động.** Vui lòng chạy `uvicorn server:app --port 8000`.'
          : 'Đã xảy ra lỗi khi tải file. Vui lòng thử lại.',
      },
      { status: 200 }
    );
  }
}
