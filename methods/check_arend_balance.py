import logging
import disnake
from methods.settings import Settings
from typing import Optional

logger = logging.getLogger(__name__)

async def get_arend_balance(inter: disnake.Interaction, settings: Settings) -> Optional[int]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        balance = await conn.execute_fetchall("SELECT balance FROM arend WHERE id=?", (inter.author.id,))
        balance = balance[0][0]
        return balance
    except Exception as e:
        logger.error(f"Get arend balance function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
        
