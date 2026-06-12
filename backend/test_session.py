import asyncio
import os
import json
from chatbot.session_store import SessionStore

async def main():
    store = SessionStore("redis://localhost:6379/0")
    await store.connect()
    try:
        # PING Redis
        await store._redis.ping()
    except Exception:
        print("Redis not running. Skipping test.")
        return

    # test history
    sid = await store.create()
    await store.append_history(sid, "user", "Hello")
    await store.append_history(sid, "assistant", "Hi there")
    
    hist = await store.get_history(sid)
    print(f"History length: {len(hist)}")
    for msg in hist:
        print(f"  {msg['role']}: {msg['content']}")
        
    await store.delete(sid)
    await store.close()

if __name__ == "__main__":
    asyncio.run(main())
