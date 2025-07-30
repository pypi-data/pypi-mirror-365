import asyncpg
from typing import Optional
from .config import settings

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool to PostgreSQL"""
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    async def disconnect(self):
        """Close all connections in the pool"""
        if self.pool:
            await self.pool.close()
    
    async def acquire_with_user_context(self, user_id: str):
        """Acquire a connection and set the current user context for RLS"""
        async with self.pool.acquire() as conn:
            await conn.execute(f"SET app.current_user_id = '{user_id}'")
            return conn
    
    async def execute_with_user(self, user_id: str, query: str, *args):
        """Execute a query with user context"""
        async with self.pool.acquire() as conn:
            await conn.execute(f"SET app.current_user_id = '{user_id}'")
            return await conn.fetch(query, *args)
    
    async def execute_one_with_user(self, user_id: str, query: str, *args):
        """Execute a query and return one row with user context"""
        async with self.pool.acquire() as conn:
            await conn.execute(f"SET app.current_user_id = '{user_id}'")
            return await conn.fetchrow(query, *args)


db = Database()