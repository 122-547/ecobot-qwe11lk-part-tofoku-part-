import disnake
import logging
from methods.settings import Settings
from typing import Optional, List

logger = logging.getLogger(__name__)

async def get_shop_roles(settings: Settings, inter: disnake.Interaction) -> Optional[List[tuple]]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        if not inter:
            logger.warning("Inter is None -> return")
            return

        conn = await settings.get_connection()

        if not conn:
            logger.warning("Connection is None -> return")
            return

        result = await conn.execute_fetchall("SELECT id, author_id, price, count, creation_date FROM shop")
        if result:
            return result
        
        return
    except Exception as e:
        logger.error(f"Get shop roles function error: {e}")
        return
    finally:
        await settings.release_connection(conn)

        
            
        
        
        