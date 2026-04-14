from __future__ import annotations

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from backend.config.settings import settings


class DatabaseManager:
    def __init__(self) -> None:
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        if self.client is not None and self.database is not None:
            return

        self.client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        await self.client.admin.command("ping")
        self.database = self.client[settings.mongodb_db_name]

    async def disconnect(self) -> None:
        if self.client is not None:
            self.client.close()
        self.client = None
        self.database = None

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.database is None:
            raise RuntimeError("Database is not initialized. Call connect() during startup.")
        return self.database


db_manager = DatabaseManager()
