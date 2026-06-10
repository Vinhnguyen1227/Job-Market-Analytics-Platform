import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.CHATBOT_BACKEND_URL || 'http://localhost:8000';

/**
 * GET /api/chatbot/status/[jobId] - BFF firewall (Option A locked).
 *
 * Always returns HTTP 200. Failures are encoded inside the JSON body
 * as `status: "ERROR"` with a short `error` code. Frontend polling
 * only branches on the JSON `status` field, never on HTTP code.
 *
 * See slm_orchestrator_api_pipeline_guide.md §3.5.
 */
function errorBody(jobId: string, code: string, message: string) {
  return {
    job_id: jobId,
    session_id: '',
    job_type: '',
    status: 'ERROR' as const,
    result: {},
    error: code,
    error_message: message,
    created_at: '',
  };
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params;

  try {
    const upstream = await fetch(`${BACKEND_URL}/api/job/${jobId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (upstream.status === 404) {
      return NextResponse.json(
        errorBody(jobId, 'job_not_found', 'Không tìm thấy job, có thể đã hết hạn.'),
        { status: 200 }
      );
    }

    if (!upstream.ok) {
      let detail = '';
      try {
        const j = await upstream.json();
        detail = j?.detail?.error_message || j?.detail || '';
      } catch {
        detail = await upstream.text();
      }
      console.error(`Job status upstream ${upstream.status}: ${detail}`);
      return NextResponse.json(
        errorBody(jobId, 'upstream_error', detail || 'Backend lỗi khi đọc trạng thái.'),
        { status: 200 }
      );
    }

    const data = await upstream.json();
    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    const isConnectionError =
      error instanceof TypeError && (error as any).cause?.code === 'ECONNREFUSED';
    console.error('Job status proxy error:', error);
    return NextResponse.json(
      errorBody(
        jobId,
        isConnectionError ? 'backend_unreachable' : 'bff_crash',
        isConnectionError
          ? 'Chatbot backend chưa khởi động.'
          : 'Lỗi kết nối tới chatbot backend.'
      ),
      { status: 200 }
    );
  }
}
