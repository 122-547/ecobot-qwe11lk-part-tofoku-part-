import aiosqlite
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class Settings:
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.pool: List[aiosqlite.Connection] = []
        self.inited = False
        self.db_path = "dbs/database.db"

    async def init(self) -> Optional[bool]:
        try:
            if self.inited:
                return
            
            for _ in range(self.pool_size):
                conn = await aiosqlite.connect(self.db_path)
                self.pool.append(conn)

            logger.info("Connection pool inititalized")
            self.inited = True
            return True

        except Exception as e:
            logger.error(f"Initializing connectoin pool function error: {e}")
            await self.close_all()
            raise

    async def get_connection(self) -> Optional[aiosqlite.Connection]:
            try:
                if not self.pool:
                    await self.init()
                if not self.pool:
                    return

                return self.pool.pop()
            except Exception as e:
                logger.error(f"Get connection function error: {e}")
                return
        
    async def release_connection(self, conn: aiosqlite.Connection):
        try:
            self.pool.append(conn)
        except Exception as e:
            logger.error(f"Release connection function error: {e}")

    async def close_all(self):
        try:
            for conn in self.pool:
                await conn.close()
            self.pool.clear()
        except Exception as e:
            logger.error(f"Close all connections function error: {e}")
