"""MongoDB Client - Persistent storage for chat history and raw CVs.

Uses Motor for async MongoDB access.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

logger = logging.getLogger(__name__)

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://admin:secret_password_123@localhost:27017")
DB_NAME = "chatbot"

class MongoClient:
    """Async wrapper around MongoDB."""

    def __init__(self):
        self._client: AsyncIOMotorClient | None = None
        self._db = None
        self._fs: AsyncIOMotorGridFSBucket | None = None

    async def connect(self):
        """Initialize MongoDB connection."""
        if self._client is None:
            self._client = AsyncIOMotorClient(MONGODB_URI)
            self._db = self._client[DB_NAME]
            self._fs = AsyncIOMotorGridFSBucket(self._db)
            
            # Ensure indexes
            await self._db.history.create_index(
                [("session_id", 1), ("timestamp", 1)]
            )
            await self._db.sessions.create_index(
                [("session_id", 1)], unique=True
            )
            
            logger.info("MongoClient connected to MongoDB.")

    async def close(self):
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._fs = None

    async def save_history_message(self, session_id: str, role: str, content: str, timestamp: float):
        """Append a single message to MongoDB history collection."""
        await self.connect()
        doc = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": timestamp,
        }
        await self._db.history.insert_one(doc)

    async def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """Retrieve full conversation history for a session."""
        await self.connect()
        cursor = self._db.history.find({"session_id": session_id}).sort("timestamp", 1)
        history = []
        async for doc in cursor:
            history.append({
                "role": doc["role"],
                "content": doc["content"],
            })
        return history

    async def update_session_cv(self, session_id: str, resume_id: str, resume_dict: dict, resume_name: str):
        """Update session record with parsed CV data."""
        await self.connect()
        await self._db.sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "resume_id": resume_id,
                    "resume_dict": resume_dict,
                    "resume_name": resume_name,
                }
            },
            upsert=True
        )

    async def get_session_cv(self, session_id: str) -> dict | None:
        """Get CV data for a session."""
        await self.connect()
        doc = await self._db.sessions.find_one({"session_id": session_id})
        if doc:
            return {
                "resume_id": doc.get("resume_id"),
                "resume_dict": doc.get("resume_dict"),
                "resume_name": doc.get("resume_name"),
            }
        return None

    async def upload_pdf(self, session_id: str, filename: str, content: bytes) -> str:
        """Upload raw PDF to GridFS and link to session."""
        await self.connect()
        file_id = await self._fs.upload_from_stream(
            filename,
            content,
            metadata={"session_id": session_id, "content_type": "application/pdf"}
        )
        return str(file_id)

    async def save_conversation_summary(self, session_id: str, summary: str):
        """Save a rolling summary of older messages."""
        await self.connect()
        await self._db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"conversation_summary": summary}},
            upsert=True
        )

    async def get_conversation_summary(self, session_id: str) -> str | None:
        """Get the saved conversation summary."""
        await self.connect()
        doc = await self._db.sessions.find_one({"session_id": session_id}, {"conversation_summary": 1})
        if doc:
            return doc.get("conversation_summary")
        return None

mongo_client = MongoClient()
