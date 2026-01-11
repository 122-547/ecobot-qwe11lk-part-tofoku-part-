import disnake
from methods.settings import Settings
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

async def get_personal_roles(inter: disnake.Interaction, settings: Settings) -> Optional[List[int]]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        my_roles = await conn.execute_fetchall("SELECT id FROM roles WHERE author_id=?", (inter.author.id,))
        my_roles = [i[0] for i in my_roles]
        return my_roles
    except Exception as e:
        logger.error(f"Get personal roles function error: {e}")
        return
    finally:
        await settings.release_connection(conn)