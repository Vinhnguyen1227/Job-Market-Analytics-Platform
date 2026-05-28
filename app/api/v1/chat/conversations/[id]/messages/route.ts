import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';
import {
  getConversation,
  appendMessage,
  appendMessages,
} from '@/backend/mongodb/chatService';
import type { MessageRole } from '@/backend/mongodb/chatService';

interface RouteParams {
  params: Promise<{ id: string }>;
}

// ─────────────────────────────────────────────────────────────
// GET /api/v1/chat/conversations/[id]/messages
// Lấy danh sách messages trong một conversation.
// Query: ?limit=50&skip=0
// ─────────────────────────────────────────────────────────────
export async function GET(request: NextRequest, { params }: RouteParams) {
  try {
    const { id } = await params;
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const conversation = await getConversation(id, user.id);
    if (!conversation) {
      return NextResponse.json(
        { error: 'Conversation không tồn tại hoặc không có quyền truy cập' },
        { status: 404 }
      );
    }

    // Hỗ trợ phân trang nhẹ — slice trên mảng đã có
    const { searchParams } = new URL(request.url);
    const limit = Math.min(parseInt(searchParams.get('limit') ?? '50'), 200);
    const skip = Math.max(parseInt(searchParams.get('skip') ?? '0'), 0);

    const messages = conversation.messages.slice(skip, skip + limit);

    return NextResponse.json({
      messages,
      total: conversation.messages.length,
      limit,
      skip,
    });
  } catch (err) {
    console.error('[GET /conversations/[id]/messages]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─────────────────────────────────────────────────────────────
// POST /api/v1/chat/conversations/[id]/messages
// Thêm message (hoặc nhiều messages cùng lúc) vào conversation.
//
// Body — gửi 1 message:
// {
//   "role": "user",
//   "content": "Hãy đánh giá CV của tôi",
//   "attachment": {                         ← optional
//     "fileName": "NguyenVanA_CV.pdf",
//     "filePath": "user-id/1234_NguyenVanA_CV.pdf",
//     "fileSize": 204800,
//     "fileType": "application/pdf",
//     "signedUrl": "https://...",
//     "uploadedAt": "2026-05-16T..."
//   }
// }
//
// Body — gửi nhiều messages (user + assistant cùng lúc):
// {
//   "messages": [
//     { "role": "user", "content": "..." },
//     { "role": "assistant", "content": "..." }
//   ]
// }
// ─────────────────────────────────────────────────────────────
export async function POST(request: NextRequest, { params }: RouteParams) {
  try {
    const { id } = await params;
    const supabase = await createClient();
    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json({ error: 'Body không hợp lệ' }, { status: 400 });
    }

    if (typeof body !== 'object' || body === null) {
      return NextResponse.json({ error: 'Body phải là object' }, { status: 400 });
    }

    const bodyObj = body as Record<string, unknown>;

    // ── Trường hợp gửi nhiều messages cùng lúc ──────────────
    if (Array.isArray(bodyObj.messages)) {
      const inputs = bodyObj.messages as Array<Record<string, unknown>>;

      if (inputs.length === 0) {
        return NextResponse.json(
          { error: 'messages không được rỗng' },
          { status: 400 }
        );
      }

      for (const m of inputs) {
        if (!m.content || typeof m.content !== 'string') {
          return NextResponse.json(
            { error: 'Mỗi message phải có content là string' },
            { status: 400 }
          );
        }
      }

      const updated = await appendMessages(
        id,
        user.id,
        inputs.map((m) => ({
          role: (m.role as MessageRole) ?? 'user',
          content: (m.content as string).trim(),
          attachment: (m.attachment as never) ?? null,
          metadata: (m.metadata as Record<string, unknown>) ?? undefined,
        }))
      );

      if (!updated) {
        return NextResponse.json(
          { error: 'Conversation không tồn tại hoặc không có quyền truy cập' },
          { status: 404 }
        );
      }

      return NextResponse.json({ conversation: updated }, { status: 201 });
    }

    // ── Trường hợp gửi 1 message ─────────────────────────────
    const { role, content, attachment, metadata } = bodyObj;

    if (!content || typeof content !== 'string') {
      return NextResponse.json(
        { error: 'content là bắt buộc và phải là string' },
        { status: 400 }
      );
    }

    const updated = await appendMessage(id, user.id, {
      role: (role as MessageRole) ?? 'user',
      content: (content as string).trim(),
      attachment: (attachment as never) ?? null,
      metadata: (metadata as Record<string, unknown>) ?? undefined,
    });

    if (!updated) {
      return NextResponse.json(
        { error: 'Conversation không tồn tại hoặc không có quyền truy cập' },
        { status: 404 }
      );
    }

    return NextResponse.json({ conversation: updated }, { status: 201 });
  } catch (err) {
    console.error('[POST /conversations/[id]/messages]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
