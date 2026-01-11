from methods.settings import Settings
from typing import Optional
import logging
from methods.get_role_data import get_role_data

logger = logging.getLogger(__name__)

async def start_selling(role_id: int, settings: Settings, price: int) -> Optional[bool]:
    try:
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        await conn.execute("UPDATE roles SET price=? WHERE id=?", (price, role_id))
        await conn.commit()
        if not settings:
            logger.warning("Settings is None -> return")
            return
        data = await get_role_data(role_id, settings)
        if not data:
            logger.warning("Data is None -> return")
            return
        
        await conn.execute("INSERT INTO shop (id, author_id, price, count, creation_date) VALUES (?, ?, ?, ?, ?)", data)
        await conn.commit()
        return True
    except Exception as e:
        logger.error(f"Start selling function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
