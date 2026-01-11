from methods.settings import Settings
import logging
from typing import Optional
import disnake

logger = logging.getLogger(__name__)

async def check_empty_slots_inventory(inter: disnake.Interaction, settings: Settings) -> Optional[bool]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        slots = await conn.execute_fetchall("SELECT * FROM inventory WHERE id=?", (inter.author.id,))
        slots = slots[0][1:]
        return None in slots
    
    except Exception as e:
        logger.error(f"Check empty slots in inventory function error: {e}")
        return
    finally:
        await settings.release_connection(conn)