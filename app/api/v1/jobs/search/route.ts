import { NextRequest, NextResponse } from 'next/server';
import { Client } from '@elastic/elasticsearch';

const esClient = new Client({
  node: process.env.ELASTICSEARCH_NODE || 'http://localhost:9200',
});

const INDEX = 'jobs';

// GET /api/v1/jobs/search
export async function GET(req: NextRequest) {
  try {
    const { searchParams } = req.nextUrl;
    const keyword       = searchParams.get('keyword')?.trim() || '';
    const locations     = searchParams.getAll('locations');
    const categories    = searchParams.getAll('categories');
    const workTypes     = searchParams.getAll('workTypes');
    const levels        = searchParams.getAll('levels');
    const experiences   = searchParams.getAll('experiences');
    const salaryBuckets = searchParams.getAll('salaryBuckets');
    const page          = Math.max(1, parseInt(searchParams.get('page') || '1'));
    const limit         = 20;
    const from          = (page - 1) * limit;

    // ─── Build Elasticsearch Bool Query ─────────────────────────────────────
    const must: any[]   = [];
    const filter: any[] = [];

    // Full-text search trên tiêu đề và tên công ty
    if (keyword) {
      must.push({
        multi_match: {
          query:  keyword,
          fields: ['tieu_de^3', 'cong_ty^2'], // tiêu đề quan trọng hơn
          type:   'best_fields',
          fuzziness: 'AUTO', // chấp nhận gõ sai chính tả nhẹ
        },
      });
    }

    // Lọc chính xác bằng term filter (nhanh hơn nhiều so với match)
    if (locations.length)     filter.push({ terms: { cities:        locations } });
    if (categories.length)    filter.push({ terms: { categories:    categories } });
    if (workTypes.length)     filter.push({ terms: { workTypes:     workTypes } });
    if (levels.length)        filter.push({ terms: { levels:        levels } });
    if (experiences.length)   filter.push({ terms: { expBuckets:    experiences } });
    if (salaryBuckets.length) filter.push({ terms: { salaryBuckets: salaryBuckets } });

    // ─── Execute Search ───────────────────────────────────────────────────────
    const result = await esClient.search({
      index: INDEX,
      from,
      size:  limit,
      sort:  must.length > 0
        ? ['_score', { created_at: 'desc' }]  // Nếu có keyword → ưu tiên relevance score
        : [{ created_at: 'desc' }],            // Không có keyword → sắp theo mới nhất
      query: {
        bool: {
          must:   must.length   > 0 ? must   : [{ match_all: {} }],
          filter: filter.length > 0 ? filter : [],
        },
      },
      _source: ['raw_data'], // Chỉ lấy raw_data để trả về cho UI
    });

    const hits  = result.hits.hits;
    const total = typeof result.hits.total === 'object'
      ? result.hits.total.value
      : result.hits.total ?? 0;

    const jobs       = hits.map((h: any) => h._source?.raw_data ?? h._source);
    const totalPages = Math.ceil(total / limit) || 1;

    return NextResponse.json({ jobs, total, page, totalPages }, {
      headers: { 'Cache-Control': 'no-store' },
    });

  } catch (err: any) {
    console.error('[/api/v1/jobs/search] Error:', err?.message ?? err);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
