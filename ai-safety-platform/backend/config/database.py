from __future__ import annotations

import asyncio
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

        max_retries = 5
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                self.client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
                await self.client.admin.command("ping")
                self.database = self.client[settings.mongodb_db_name]
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Database connection attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 10)
                else:
                    raise RuntimeError(f"Failed to connect to MongoDB after {max_retries} attempts: {e}") from e

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
