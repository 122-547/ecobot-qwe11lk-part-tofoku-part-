import disnake
from methods.settings import Settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def unequip_role(inter: disnake.Interaction, settings: Settings, role_id: int) -> Optional[bool]:
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
        slots = await conn.execute_fetchall("SELECT * FROM equipped WHERE id=?", (inter.author.id,))
        slots = slots[0][1:]
        slot_num = slots.index(role_id)+1
        query = f"UPDATE equipped SET [{str(slot_num)}]=NULL WHERE id=?"
        await conn.execute(query, (inter.author.id,))

        role = inter.guild.get_role(role_id)
        if not role:
            logger.warning("Role is None -> return")
            return
        await inter.author.remove_roles(role)

        await conn.commit()
        return True
    
    except Exception as e:
        logger.error(f"Unequip role function error: {e}")
        return
    finally:
        await settings.release_connection(conn)