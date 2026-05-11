/**
 * Sync script: Pull all jobs from Supabase → pre-process → index into Elasticsearch.
 * Run with: npm run es:sync
 */
import { createClient } from '@supabase/supabase-js';
import { Client } from '@elastic/elasticsearch';
import dotenv from 'dotenv';
import {
  isValidInfo, splitLocations, getSalaryBuckets,
  getExpBuckets, getWorkTypeTags, getLevels,
} from './helpers';

dotenv.config({ path: '.env.local' });

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const esClient = new Client({
  node: process.env.ELASTICSEARCH_NODE || 'http://localhost:9200',
});

const INDEX = 'jobs';

// ─── 1. Tạo/cập nhật mapping của index ────────────────────────────────────────

async function ensureIndex() {
  const exists = await esClient.indices.exists({ index: INDEX });
  if (exists) {
    console.log(`[ES] Index "${INDEX}" đã tồn tại, bỏ qua bước tạo mới.`);
    return;
  }

  await esClient.indices.create({
    index: INDEX,
    mappings: {
      properties: {
        url:           { type: 'keyword' },
        tieu_de:       { type: 'text', analyzer: 'standard' },
        cong_ty:       { type: 'text', analyzer: 'standard' },
        cities:        { type: 'keyword' },
        categories:    { type: 'keyword' },
        workTypes:     { type: 'keyword' },
        levels:        { type: 'keyword' },
        expBuckets:    { type: 'keyword' },
        salaryBuckets: { type: 'keyword' },
        created_at:    { type: 'date' },
        raw_data:      { type: 'object', enabled: false }, // stored but not indexed
      },
    },
  });
  console.log(`[ES] Đã tạo index "${INDEX}" thành công.`);
}

// ─── 2. Chuyển đổi 1 job thành document ES ─────────────────────────────────────

function toEsDoc(job: any) {
  return {
    url:           job.url || '',
    tieu_de:       job.tieu_de || job.title || '',
    cong_ty:       job.cong_ty || job.company || '',
    cities:        splitLocations(job.dia_diem || job.location || '').filter(isValidInfo),
    categories:    (job.nganh_nghe || '').split(',').map((c: string) => c.trim()).filter(isValidInfo),
    workTypes:     getWorkTypeTags(job.hinh_thuc_lam_viec),
    levels:        getLevels(job.cap_bac),
    expBuckets:    getExpBuckets(job.kinh_nghiem_lam_viec),
    salaryBuckets: getSalaryBuckets(job.muc_luong || job.salary),
    created_at:    job.created_at || new Date().toISOString(),
    raw_data:      job,
  };
}

// ─── 3. Bulk index vào ES ──────────────────────────────────────────────────────

async function bulkIndex(jobs: any[]) {
  if (jobs.length === 0) return;

  const operations = jobs.flatMap(job => [
    { index: { _index: INDEX, _id: job.url || job.id } },
    toEsDoc(job),
  ]);

  const result = await esClient.bulk({ operations, refresh: true });

  const erroredDocs = result.items.filter((item: any) => item.index?.error);
  if (erroredDocs.length > 0) {
    console.error(`[ES] ${erroredDocs.length} documents bị lỗi khi index.`);
  }
  return result.items.length - erroredDocs.length;
}

// ─── 4. Main: Kéo toàn bộ từ Supabase và sync ─────────────────────────────────

async function syncAll() {
  console.log('=== BẮT ĐẦU SYNC SUPABASE → ELASTICSEARCH ===\n');

  await ensureIndex();

  let offset = 0;
  const batchSize = 500;
  let totalSynced = 0;
  let totalFetched = 0;

  // Deduplication
  const seenUrls = new Set<string>();

  while (true) {
    console.log(`[Supabase] Đang lấy batch ${offset / batchSize + 1} (offset: ${offset})...`);

    const { data, error } = await supabase
      .from('jobs')
      .select('*')
      .order('created_at', { ascending: false })
      .range(offset, offset + batchSize - 1);

    if (error) { console.error('[Supabase] Lỗi:', error); break; }
    if (!data || data.length === 0) break;

    // Deduplicate
    const unique = data.filter(job => {
      const key = job.url || `${job.tieu_de}-${job.cong_ty}`;
      if (!key || seenUrls.has(key)) return false;
      seenUrls.add(key);
      return true;
    });

    totalFetched += data.length;

    const synced = await bulkIndex(unique);
    totalSynced += synced ?? 0;
    console.log(`[ES] Đã index ${synced} / ${unique.length} documents (batch ${offset / batchSize + 1})`);

    if (data.length < batchSize) break;
    offset += batchSize;
  }

  console.log(`\n=== HOÀN TẤT: Lấy ${totalFetched} từ Supabase → Index ${totalSynced} vào Elasticsearch ===`);
  process.exit(0);
}

syncAll().catch(err => {
  console.error('[FATAL]', err);
  process.exit(1);
});
