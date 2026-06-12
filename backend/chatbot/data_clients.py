"""Data clients - Elasticsearch jobs + Qdrant resumes.

ES `jobs` index uses Vietnamese field names (tieu_de, cong_ty, cities,
salaryBuckets, expBuckets, workTypes). Payload `_source.raw_data`
holds the full nested job document the scraper produced.

Qdrant `resumes` collection (Phase 4) stores 4 named vectors per resume
plus the full canonical JSON in `payload.resume`.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from elasticsearch import AsyncElasticsearch
from qdrant_client import QdrantClient as QdrantClientLib

logger = logging.getLogger(__name__)


# Salary buckets used by the scraper / index (millions VND).
SALARY_BUCKETS = [
    "Dưới 10 triệu",
    "10 - 15 triệu",
    "15 - 20 triệu",
    "20 - 25 triệu",
    "25 - 30 triệu",
    "30 - 50 triệu",
    "Trên 50 triệu",
    "Thỏa thuận",
]

BUCKET_RANGES = [
    (0, 10, "Dưới 10 triệu"),
    (10, 15, "10 - 15 triệu"),
    (15, 20, "15 - 20 triệu"),
    (20, 25, "20 - 25 triệu"),
    (25, 30, "25 - 30 triệu"),
    (30, 50, "30 - 50 triệu"),
    (50, 200, "Trên 50 triệu"),
]


def _buckets_for_range(min_s: int | None, max_s: int | None) -> list[str]:
    if min_s is None and max_s is None:
        return []
    lo = min_s if min_s is not None else 0
    hi = max_s if max_s is not None else 200
    out = []
    for b_lo, b_hi, name in BUCKET_RANGES:
        if b_hi >= lo and b_lo <= hi:
            out.append(name)
    return out


class ElasticsearchClient:
    """Async wrapper around the `jobs` index."""

    INDEX = "jobs"

    def __init__(self):
        node = os.environ.get("ELASTICSEARCH_NODE", "http://elasticsearch:9200")
        self._client = AsyncElasticsearch(node)

    async def health(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception as e:
            logger.warning(f"Elasticsearch ping failed: {e}")
            return False

    async def close(self):
        await self._client.close()

    async def search_jobs(self, params: dict[str, Any], limit: int = 8) -> list[dict]:
        """Run a job search using validated tool params.

        Returns a list of `raw_data` dicts (full job documents).
        """
        keyword = params.get("keyword")
        location = params.get("location")
        experience = params.get("experience")
        work_type = params.get("work_type")
        min_salary = params.get("min_salary")
        max_salary = params.get("max_salary")

        must: list[dict] = []
        filt: list[dict] = []

        if keyword:
            must.append({
                "multi_match": {
                    "query": keyword,
                    "fields": ["tieu_de^3", "cong_ty^2"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            })
        if location:
            filt.append({"terms": {"cities": [location]}})
        if experience:
            filt.append({"terms": {"expBuckets": [experience]}})
        if work_type:
            filt.append({"terms": {"workTypes": [work_type]}})
        buckets = _buckets_for_range(min_salary, max_salary)
        if buckets:
            filt.append({"terms": {"salaryBuckets": buckets}})

        body = {
            "from": 0,
            "size": limit,
            "sort": ["_score", {"created_at": "desc"}] if must else [{"created_at": "desc"}],
            "query": {
                "bool": {
                    "must": must or [{"match_all": {}}],
                    "filter": filt,
                }
            },
            "_source": ["raw_data"],
        }

        try:
            res = await self._client.search(index=self.INDEX, body=body)
        except Exception as e:
            logger.error(f"ES search failed: {e}")
            return []

        out = []
        for h in res["hits"]["hits"]:
            src = h.get("_source", {}) or {}
            raw = src.get("raw_data") or src
            out.append(raw)
        return out

    async def get_distinct_cities(self) -> list[str]:
        body = {"size": 0, "aggs": {"distinct_cities": {"terms": {"field": "cities", "size": 1000}}}}
        try:
            res = await self._client.search(index=self.INDEX, body=body)
            buckets = res.get("aggregations", {}).get("distinct_cities", {}).get("buckets", [])
            return [b["key"] for b in buckets]
        except Exception as e:
            logger.error(f"ES aggs failed for cities: {e}")
            return []

    async def get_distinct_exp_buckets(self) -> list[str]:
        body = {"size": 0, "aggs": {"distinct_exp": {"terms": {"field": "expBuckets", "size": 100}}}}
        try:
            res = await self._client.search(index=self.INDEX, body=body)
            buckets = res.get("aggregations", {}).get("distinct_exp", {}).get("buckets", [])
            return [b["key"] for b in buckets]
        except Exception as e:
            logger.error(f"ES aggs failed for expBuckets: {e}")
            return []

    async def get_distinct_work_types(self) -> list[str]:
        body = {"size": 0, "aggs": {"distinct_work_types": {"terms": {"field": "workTypes", "size": 100}}}}
        try:
            res = await self._client.search(index=self.INDEX, body=body)
            buckets = res.get("aggregations", {}).get("distinct_work_types", {}).get("buckets", [])
            return [b["key"] for b in buckets]
        except Exception as e:
            logger.error(f"ES aggs failed for workTypes: {e}")
            return []


class ResumeQdrantClient:
    """Resume vector store reader.

    Phase 4 writes via ResumeVectorStore. Here we only need to
    fetch a stored resume by `resume_id` and (optionally) do a
    naive skill-gap diff against a JD text.
    """

    COLLECTION = "resumes"

    def __init__(self):
        url = os.environ.get("QDRANT_URL")
        if url:
            self._client = QdrantClientLib(url=url)
        else:
            path = os.environ.get("QDRANT_PATH", "data/qdrant_db")
            self._client = QdrantClientLib(path=path)

    def health(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception as e:
            logger.warning(f"Qdrant ping failed: {e}")
            return False

    def get_resume(self, resume_id: str) -> dict | None:
        try:
            pts = self._client.retrieve(
                collection_name=self.COLLECTION,
                ids=[resume_id],
                with_payload=True,
            )
        except Exception as e:
            logger.error(f"Qdrant retrieve failed: {e}")
            return None
        if not pts:
            return None
        payload = pts[0].payload or {}
        return payload.get("resume") or payload

    def skill_set(self, resume_id: str) -> list[str]:
        try:
            pts = self._client.retrieve(
                collection_name=self.COLLECTION,
                ids=[resume_id],
                with_payload=True,
            )
        except Exception:
            return []
        if not pts:
            return []
        payload = pts[0].payload or {}
        skills_flat = payload.get("skills_flat")
        if isinstance(skills_flat, list):
            return [str(s) for s in skills_flat]
        if isinstance(skills_flat, str):
            return [s.strip() for s in skills_flat.split(",") if s.strip()]
        return []

    def compare_skills(self, resume_id: str, jd_text: str) -> dict:
        """Cheap skill-gap diff: token overlap on the JD text vs payload skills."""
        have = {s.lower() for s in self.skill_set(resume_id)}
        if not have:
            return {"have": [], "missing": [], "jd_excerpt": jd_text[:500]}

        # Naive: a JD "needs" a skill name iff that skill name appears in the JD text.
        jd_low = jd_text.lower()
        missing = sorted(s for s in have if s not in jd_low)
        present = sorted(s for s in have if s in jd_low)
        return {
            "have": sorted(have),
            "present_in_jd": present,
            "missing": missing,
            "jd_excerpt": jd_text[:500],
        }


# Module-level singletons used by the dispatcher / health probe.
es_client = ElasticsearchClient()
qdrant_client = ResumeQdrantClient()
