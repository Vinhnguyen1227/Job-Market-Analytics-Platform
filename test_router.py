import asyncio
import os
import sys

# Add backend dir to path so we can import
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'chatbot'))

from intent_router import router_route
from tool_schemas import SearchJobsParams

async def main():
    message = "BẮT BUỘC dùng tool search_jobs để trích xuất các tham số (location, company, min_salary, max_salary, experience, work_type, keyword). CHÚ Ý: Phải tách riêng location (thành phố) ra khỏi keyword. Câu tìm kiếm: backend Hanoi"
    tc = await router_route(message)
    print(f"Tool: {tc.tool}")
    print(f"Params: {tc.params}")

if __name__ == "__main__":
    asyncio.run(main())
