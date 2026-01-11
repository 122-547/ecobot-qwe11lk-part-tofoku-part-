from methods.settings import Settings
import logging
import disnake
from typing import Optional

logger = logging.getLogger(__name__)

async def buy_role(role: tuple, settings: Settings, inter: disnake.Interaction) -> Optional[bool]:
    try:
        if not role:
            logger.warning("Role is None -> return")
            return
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
        query = f"UPDATE bank SET balance=balance-{role[2]} WHERE id=?"
        await conn.execute(query, (inter.author.id,))
        query = f"UPDATE bank SET balance=balance+{role[2]} WHERE id=?"
        await conn.execute(query, (role[1],))
        slots = await conn.execute_fetchall("SELECT * FROM inventory WHERE id=?", (inter.author.id,)) # [(int), (int), (None), (...)]

        slots = slots[0][1:]

        empty_slot = slots.index(None)
        query = f"UPDATE inventory SET [{str(empty_slot+1)}]=? WHERE id=?"
        await conn.execute(query, (role[0], inter.author.id))
        await conn.execute("UPDATE shop SET count=count+1 WHERE id=?", (role[0],))
        await conn.commit()
        return True
    except Exception as e:
        logger.error(f"Buy role function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
        
        
        