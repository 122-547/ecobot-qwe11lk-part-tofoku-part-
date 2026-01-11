import disnake
from typing import Optional
import logging
from methods.settings import Settings

logger = logging.getLogger(__name__)

async def get_role_data(role_id: int, settings: Settings) -> Optional[tuple]:
    try:
        if not role_id:
            logger.warning("Role id is None -> return")
            return
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        data = await conn.execute_fetchall("SELECT id, author_id, price, count, creation_date FROM shop WHERE id=?", (role_id,))
        if not data:
            data = await conn.execute_fetchall("SELECT id, author_id, price, count, creation_date FROM roles WHERE id=?", (role_id,))
        data = data[0]
        return data
    except Exception as e:
        logger.error(f"Get role data function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
