import logging
from typing import Optional
import disnake
from methods.settings import Settings

logger = logging.getLogger(__name__)


async def delete_role(role_id: int, inter: disnake.Interaction, settings: Settings) -> Optional[bool]:
    try:
        user = inter.author
        if not user:
            logger.warning("User is None -> return")
            return
        guild = inter.author.guild
        if not guild:
            logger.warning("Guild is None -> return")
            return
        role = guild.get_role(role_id)
        if not role:
            logger.warning("Role is None -> return")
            return
        name = role.name
        await role.delete()
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        await conn.execute("DELETE FROM roles WHERE id=?", (role_id,))
        await conn.execute("DELETE FROM shop WHERE id=?", (role_id,))
        conditions = [f'"{i}"={role_id}' for i in range(1, 21)]
        query = f'SELECT * FROM inventory WHERE {" OR ".join(conditions)}'
        inventory = await conn.execute_fetchall(query)
        if not inventory:
            logger.warning("Inventory is None -> return")
            return
        for user in inventory:
            user_inv = user[1:]
            slot = user_inv.index(role_id)+1
            query = f"UPDATE inventory SET [{str(slot)}]=NULL WHERE id=?"
            await conn.execute(query, (user[0],))
        query = f'SELECT * FROM equipped WHERE {" OR ".join(conditions)}'
        equipped = await conn.execute_fetchall(query)
        if not equipped:
            logger.warning("Equipped is None -> return")
            return
        for user in equipped:
            user_eq = user[1:]
            slot = user_eq.index(role_id)+1
            query = f"UPDATE inventory SET [{str(slot)}]=NULL WHERE id=?"
            await conn.execute(query, (user[0],))
        
        await conn.commit()
        return True

    except Exception as e:
        logger.error(f"Delete role function error: {e}")
        return
    finally:
        await settings.release_connection(conn)