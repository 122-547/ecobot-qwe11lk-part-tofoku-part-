from methods.settings import Settings
from typing import Optional
import logging
from methods.get_role_data import get_role_data

logger = logging.getLogger(__name__)

async def stop_selling(role_id: int, settings: Settings) -> Optional[bool]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        data = await get_role_data(role_id, settings)
        if not data:
            logger.warning("Data is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        await conn.execute("DELETE FROM shop WHERE id=?", (role_id,))
        await conn.execute("UPDATE roles SET price=?, count=? WHERE id=?", (data[2], data[3], role_id))
        await conn.commit()
        return True

    except Exception as e:
        logger.error(f"Start selling function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
