import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';
import { createConversation, listConversations } from '@/backend/mongodb/chatService';
import type { NewMessageInput } from '@/backend/mongodb/types';

// ─────────────────────────────────────────────────────────────
// GET /api/v1/chat/conversations
// Lấy danh sách conversations của user đang đăng nhập.
// Query params: ?limit=20&skip=0
// ─────────────────────────────────────────────────────────────
export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const limit = Math.min(parseInt(searchParams.get('limit') ?? '20'), 100);
    const skip = Math.max(parseInt(searchParams.get('skip') ?? '0'), 0);

    const conversations = await listConversations(user.id, limit, skip);

    return NextResponse.json({ conversations, total: conversations.length });
  } catch (err) {
    console.error('[GET /conversations]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─────────────────────────────────────────────────────────────
// POST /api/v1/chat/conversations
// Tạo conversation mới.
// Body (optional):
// {
//   "message": {
//     "role": "user",
//     "content": "Xin chào",
//     "attachment": { ...CvAttachment }   ← optional
//   }
// }
// ─────────────────────────────────────────────────────────────
export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    let firstMessage: NewMessageInput | undefined;

    // Body là optional — có thể tạo conversation trống
    try {
      const body = await request.json();
      if (body?.message) {
        const { role, content, attachment, metadata } = body.message;

        if (!content || typeof content !== 'string') {
          return NextResponse.json(
            { error: 'message.content là bắt buộc và phải là string' },
            { status: 400 }
          );
        }

        firstMessage = {
          role: role ?? 'user',
          content: content.trim(),
          attachment: attachment ?? null,
          metadata: metadata ?? undefined,
        };
      }
    } catch {
      // Body rỗng hoặc không phải JSON — OK, tạo conversation trống
    }

    const conversation = await createConversation(user.id, firstMessage);

    return NextResponse.json({ conversation }, { status: 201 });
  } catch (err) {
    console.error('[POST /conversations]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
