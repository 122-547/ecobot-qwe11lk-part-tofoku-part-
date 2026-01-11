import disnake 
from methods.settings import Settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def get_quipped_status(inter: disnake.Interaction, settings: Settings, role_id: int) -> Optional[bool]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        equip = await conn.execute_fetchall("SELECT * FROM equipped WHERE id=?", (inter.author.id,))
        if not equip:
            logger.warning("Equip is None -> return")
            return
        equip = equip[0][1:]
        return role_id in equip
    
    except Exception as e:
        logger.error(f"Get equipped status function error: {e}")
        return
    finally:
        await settings.release_connection(conn)