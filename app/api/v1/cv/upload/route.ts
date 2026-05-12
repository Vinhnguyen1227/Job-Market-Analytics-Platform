import { createClient } from '@/backend/supabase/server';
import { NextRequest, NextResponse } from 'next/server';

const ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
];

const MAX_SIZE_BYTES = 5 * 1024 * 1024; // 5MB

export async function POST(req: NextRequest) {
  const supabase = await createClient();

  // Kiểm tra xác thực
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json({ error: 'Invalid form data' }, { status: 400 });
  }

  const file = formData.get('file') as File | null;
  if (!file) {
    return NextResponse.json({ error: 'Không tìm thấy file' }, { status: 400 });
  }

  // Validate loại file
  if (!ALLOWED_TYPES.includes(file.type)) {
    return NextResponse.json(
      { error: 'Chỉ chấp nhận file PDF, DOC, DOCX' },
      { status: 400 }
    );
  }

  // Validate kích thước
  if (file.size > MAX_SIZE_BYTES) {
    return NextResponse.json(
      { error: 'File vượt quá 5MB' },
      { status: 400 }
    );
  }

  // Tạo đường dẫn: {userId}/{timestamp}_{tên file an toàn}
  const safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
  const filePath = `${user.id}/${Date.now()}_${safeName}`;

  const bytes = await file.arrayBuffer();

  // Upload lên Supabase Storage bucket "user-cvs"
  const { error: uploadError } = await supabase.storage
    .from('user-cvs')
    .upload(filePath, bytes, {
      contentType: file.type,
      upsert: true,
    });

  if (uploadError) {
    console.error('[CV Upload] Storage error:', uploadError.message);
    return NextResponse.json(
      { error: `Lỗi upload: ${uploadError.message}` },
      { status: 500 }
    );
  }

  // Lấy signed URL (private bucket — expires sau 1 năm)
  const { data: signedData, error: signedError } = await supabase.storage
    .from('user-cvs')
    .createSignedUrl(filePath, 60 * 60 * 24 * 365);

  if (signedError || !signedData) {
    return NextResponse.json(
      { error: 'Upload thành công nhưng không lấy được URL' },
      { status: 500 }
    );
  }

  // Lưu metadata vào user_metadata (Supabase Auth)
  const cvMeta = {
    file_name: file.name,
    file_path: filePath,
    file_size: file.size,
    file_type: file.type,
    uploaded_at: new Date().toISOString(),
    signed_url: signedData.signedUrl,
  };

  const { error: updateError } = await supabase.auth.updateUser({
    data: { cv: cvMeta },
  });

  if (updateError) {
    console.error('[CV Upload] Metadata update error:', updateError.message);
    // Upload vẫn thành công, chỉ metadata lưu thất bại — không block
  }

  return NextResponse.json({
    success: true,
    fileName: file.name,
    fileSize: file.size,
    fileType: file.type,
    signedUrl: signedData.signedUrl,
    filePath,
  });
}

// Lấy thông tin CV hiện tại của user
export async function GET() {
  const supabase = await createClient();

  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const cvMeta = user.user_metadata?.cv ?? null;

  // Nếu có cv, refresh signed URL (vì URL có thể hết hạn)
  if (cvMeta?.file_path) {
    const { data: signedData } = await supabase.storage
      .from('user-cvs')
      .createSignedUrl(cvMeta.file_path, 60 * 60 * 24 * 365);

    return NextResponse.json({
      cv: signedData
        ? { ...cvMeta, signed_url: signedData.signedUrl }
        : cvMeta,
    });
  }

  return NextResponse.json({ cv: null });
}

// Xoá CV
export async function DELETE() {
  const supabase = await createClient();

  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const filePath = user.user_metadata?.cv?.file_path;
  if (!filePath) {
    return NextResponse.json({ error: 'Không có CV để xoá' }, { status: 404 });
  }

  const { error: removeError } = await supabase.storage
    .from('user-cvs')
    .remove([filePath]);

  if (removeError) {
    return NextResponse.json({ error: removeError.message }, { status: 500 });
  }

  // Xoá metadata
  await supabase.auth.updateUser({ data: { cv: null } });

  return NextResponse.json({ success: true });
}
