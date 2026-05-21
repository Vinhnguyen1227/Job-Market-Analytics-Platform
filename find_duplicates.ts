/**
 * Script tìm các jobs bị trùng lặp trong Supabase.
 * Chạy: npx ts-node --project tsconfig.scripts.json --transpile-only find_duplicates.ts
 */
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

async function findDuplicates() {
  console.log('Đang lấy toàn bộ jobs từ Supabase...\n');

  let allJobs: any[] = [];
  let offset = 0;
  const batchSize = 1000;

  while (true) {
    const { data, error } = await supabase
      .from('jobs')
      .select('id, url, tieu_de, cong_ty, dia_diem, created_at')
      .range(offset, offset + batchSize - 1);

    if (error || !data || data.length === 0) break;
    allJobs = allJobs.concat(data);
    if (data.length < batchSize) break;
    offset += batchSize;
  }

  console.log(`Tổng số jobs: ${allJobs.length}\n`);

  // ─── Tìm trùng theo URL ────────────────────────────────────────────────────
  const urlMap = new Map<string, any[]>();
  for (const job of allJobs) {
    const key = (job.url || '').trim().toLowerCase();
    if (!key) continue;
    if (!urlMap.has(key)) urlMap.set(key, []);
    urlMap.get(key)!.push(job);
  }

  const dupByUrl = Array.from(urlMap.entries()).filter(([, jobs]) => jobs.length > 1);

  // ─── Tìm trùng theo Tiêu đề + Công ty (không có URL) ─────────────────────
  const noUrlJobs = allJobs.filter(j => !j.url || !j.url.trim());
  const titleMap = new Map<string, any[]>();
  for (const job of noUrlJobs) {
    const key = `${(job.tieu_de || '').trim().toLowerCase()}__${(job.cong_ty || '').trim().toLowerCase()}`;
    if (!key || key === '__') continue;
    if (!titleMap.has(key)) titleMap.set(key, []);
    titleMap.get(key)!.push(job);
  }
  const dupByTitle = Array.from(titleMap.entries()).filter(([, jobs]) => jobs.length > 1);

  // ─── Kết quả ────────────────────────────────────────────────────────────────
  const totalDupUrl   = dupByUrl.reduce((sum, [, jobs]) => sum + jobs.length - 1, 0);
  const totalDupTitle = dupByTitle.reduce((sum, [, jobs]) => sum + jobs.length - 1, 0);

  console.log(`══════════════════════════════════════════════`);
  console.log(`TRÙNG THEO URL: ${dupByUrl.length} nhóm (${totalDupUrl} bản thừa)`);
  console.log(`══════════════════════════════════════════════`);
  for (const [url, jobs] of dupByUrl) {
    console.log(`\n🔗 URL: ${url}`);
    for (const j of jobs) {
      console.log(`   ID: ${j.id} | ${j.tieu_de} @ ${j.cong_ty} | created: ${j.created_at?.slice(0, 10)}`);
    }
  }

  console.log(`\n══════════════════════════════════════════════`);
  console.log(`TRÙNG THEO TIÊU ĐỀ + CÔNG TY (không URL): ${dupByTitle.length} nhóm (${totalDupTitle} bản thừa)`);
  console.log(`══════════════════════════════════════════════`);
  for (const [key, jobs] of dupByTitle) {
    const [title, company] = key.split('__');
    console.log(`\n📋 "${title}" @ "${company}"`);
    for (const j of jobs) {
      console.log(`   ID: ${j.id} | Địa điểm: ${j.dia_diem} | created: ${j.created_at?.slice(0, 10)}`);
    }
  }

  console.log(`\n══════════════════════════════════════════════`);
  console.log(`TỔNG: ${totalDupUrl + totalDupTitle} bản ghi trùng lặp cần xem xét.`);
  process.exit(0);
}

findDuplicates().catch(err => {
  console.error(err);
  process.exit(1);
});
