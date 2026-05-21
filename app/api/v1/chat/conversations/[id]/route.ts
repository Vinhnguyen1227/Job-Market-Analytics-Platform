import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/backend/supabase/server';
import {
  getConversation,
  updateConversationTitle,
  deleteConversation,
} from '@/backend/mongodb/chatService';

interface RouteParams {
  params: Promise<{ id: string }>;
}

// ─────────────────────────────────────────────────────────────
// GET /api/v1/chat/conversations/[id]
// Lấy 1 conversation cùng toàn bộ messages (kể cả attachment).
// ─────────────────────────────────────────────────────────────
export async function GET(_request: NextRequest, { params }: RouteParams) {
  try {
    const { id } = await params;
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
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

    return NextResponse.json({ conversation });
  } catch (err) {
    console.error('[GET /conversations/[id]]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─────────────────────────────────────────────────────────────
// PATCH /api/v1/chat/conversations/[id]
// Cập nhật title của conversation.
// Body: { "title": "Tên mới" }
// ─────────────────────────────────────────────────────────────
export async function PATCH(request: NextRequest, { params }: RouteParams) {
  try {
    const { id } = await params;
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    let body: { title?: string };
    try {
      body = await request.json();
    } catch {
      return NextResponse.json({ error: 'Body không hợp lệ' }, { status: 400 });
    }

    if (!body.title || typeof body.title !== 'string' || !body.title.trim()) {
      return NextResponse.json(
        { error: 'title là bắt buộc và không được để trống' },
        { status: 400 }
      );
    }

    const updated = await updateConversationTitle(id, user.id, body.title);
    if (!updated) {
      return NextResponse.json(
        { error: 'Conversation không tồn tại hoặc không có quyền chỉnh sửa' },
        { status: 404 }
      );
    }

    return NextResponse.json({ conversation: updated });
  } catch (err) {
    console.error('[PATCH /conversations/[id]]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

// ─────────────────────────────────────────────────────────────
// DELETE /api/v1/chat/conversations/[id]
// Xóa vĩnh viễn conversation (hard delete).
// ─────────────────────────────────────────────────────────────
export async function DELETE(_request: NextRequest, { params }: RouteParams) {
  try {
    const { id } = await params;
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const success = await deleteConversation(id, user.id);
    if (!success) {
      return NextResponse.json(
        { error: 'Conversation không tồn tại hoặc không có quyền xóa' },
        { status: 404 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error('[DELETE /conversations/[id]]', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
