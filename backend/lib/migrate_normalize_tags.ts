/**
 * migrate_normalize_tags.ts
 * ─────────────────────────────────────────────────────────────
 * Migration script một lần: đọc toàn bộ jobs từ Supabase,
 * chuẩn hóa field `nganh_nghe` bằng normalizeJobTags,
 * rồi update lại những record có thay đổi.
 *
 * Chạy: ts-node --project tsconfig.scripts.json --transpile-only backend/lib/migrate_normalize_tags.ts
 */

import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import { normalizeJobTags } from './normalizeJobTags';

dotenv.config({ path: '.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const PAGE_SIZE = 200;

async function fetchAllJobs(): Promise<Array<{ url: string; nganh_nghe: string | null }>> {
  const allJobs: Array<{ url: string; nganh_nghe: string | null }> = [];
  let from = 0;

  while (true) {
    const { data, error } = await supabase
      .from('jobs')
      .select('url, nganh_nghe')
      .order('url')
      .range(from, from + PAGE_SIZE - 1);

    if (error) {
      console.error('Lỗi khi fetch jobs:', error.message);
      break;
    }

    if (!data || data.length === 0) break;

    allJobs.push(...data);
    console.log(`  Đã fetch ${allJobs.length} records...`);

    if (data.length < PAGE_SIZE) break;
    from += PAGE_SIZE;
  }

  return allJobs;
}

async function run() {
  console.log('═══════════════════════════════════════════════');
  console.log('  MIGRATION: Chuẩn hóa nganh_nghe trong Supabase');
  console.log('═══════════════════════════════════════════════\n');

  console.log('[1/3] Đang fetch toàn bộ jobs...');
  const jobs = await fetchAllJobs();
  console.log(`→ Tổng: ${jobs.length} records\n`);

  console.log('[2/3] Phân tích & lọc các record cần update...');
  const toUpdate: Array<{ url: string; before: string; after: string }> = [];

  for (const job of jobs) {
    const before = job.nganh_nghe ?? 'N/A';
    const after = normalizeJobTags(before);

    if (before !== after) {
      toUpdate.push({ url: job.url, before, after });
    }
  }

  console.log(`→ Cần cập nhật: ${toUpdate.length}/${jobs.length} records\n`);

  if (toUpdate.length === 0) {
    console.log('✅ Dữ liệu đã sạch, không cần update gì thêm.');
    return;
  }

  // In preview các thay đổi
  console.log('[PREVIEW] Các thay đổi sẽ được áp dụng:');
  console.log('─'.repeat(60));
  for (const { url, before, after } of toUpdate.slice(0, 20)) {
    const shortUrl = url.replace('https://vn.joboko.com', '').slice(0, 60);
    console.log(`  URL   : ...${shortUrl}`);
    console.log(`  Before: ${before}`);
    console.log(`  After : ${after}`);
    console.log('');
  }
  if (toUpdate.length > 20) {
    console.log(`  ... và ${toUpdate.length - 20} records khác\n`);
  }

  console.log('[3/3] Đang cập nhật database...');
  let successCount = 0;
  let failCount = 0;

  for (const { url, after } of toUpdate) {
    const { error } = await supabase
      .from('jobs')
      .update({ nganh_nghe: after })
      .eq('url', url);

    if (error) {
      console.error(`  ❌ Lỗi update [${url.slice(-30)}]:`, error.message);
      failCount++;
    } else {
      successCount++;
    }
  }

  console.log('\n═══════════════════════════════════════════════');
  console.log(`  KẾT QUẢ:`);
  console.log(`  ✅ Thành công : ${successCount} records`);
  console.log(`  ❌ Thất bại  : ${failCount} records`);
  console.log('═══════════════════════════════════════════════');
}

run().catch((err) => {
  console.error('Lỗi nghiêm trọng:', err);
  process.exit(1);
});
