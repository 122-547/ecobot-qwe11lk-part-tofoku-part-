from methods.settings import Settings
import logging
import disnake
from typing import Optional, List

logger = logging.getLogger(__name__)

async def get_user_roles(inter: disnake.Interaction, settings: Settings) -> Optional[List[int]]:
    try:
        if not inter:
            logger.warning("Inter is None -> return")
            return
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        roles = await conn.execute_fetchall("SELECT * FROM inventory WHERE id=?", (inter.author.id,))
        roles = roles[0][1:]

        # for i, role in enumerate(roles):
        #     if not role[0]:
        #         roles[i] = 0
        #     else:
        #         id = role[0]
        #         roles[i] = id
        roles = [0 if not role else role for role in roles]
        roles = sorted(roles, reverse=True)
        del roles[roles.index(0):]
        return roles
    except Exception as e:
        logger.error(f"Get user roles function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
