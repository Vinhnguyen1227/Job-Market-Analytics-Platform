import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.CHATBOT_BACKEND_URL || 'http://localhost:8000';

/**
 * POST /api/kie - BFF proxy for the standalone KIE page.
 *
 * Always returns HTTP 200 (Option A firewall). Failures land in the
 * body as `{ error: <code>, error_message: <vi msg> }` so the page
 * can display a clean message without try/catch on HTTP code.
 */
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json(
        { error: 'missing_file', error_message: 'Vui lòng chọn file PDF.' },
        { status: 200 }
      );
    }

    const forward = new FormData();
    forward.append('file', file);

    const upstream = await fetch(`${BACKEND_URL}/api/kie`, {
      method: 'POST',
      body: forward,
    });

    if (!upstream.ok) {
      const text = await upstream.text();
      console.error(`KIE upstream ${upstream.status}: ${text}`);
      return NextResponse.json(
        { error: 'upstream_error', error_message: 'Backend lỗi khi xử lý CV.' },
        { status: 200 }
      );
    }

    const data = await upstream.json();
    if (!data?.job_id) {
      return NextResponse.json(
        { error: 'no_job_id', error_message: 'Backend không trả về job_id.' },
        { status: 200 }
      );
    }
    return NextResponse.json({ job_id: data.job_id, status: 'PENDING' });
  } catch (error: any) {
    const isConnectionError =
      error instanceof TypeError && (error as any).cause?.code === 'ECONNREFUSED';
    console.error('KIE proxy error:', error);
    return NextResponse.json(
      {
        error: isConnectionError ? 'backend_unreachable' : 'bff_crash',
        error_message: isConnectionError
          ? 'Chatbot backend chưa khởi động.'
          : 'Lỗi không xác định khi tải CV.',
      },
      { status: 200 }
    );
  }
}
