import disnake
import logging
from methods.settings import Settings
from typing import Optional

logger = logging.getLogger(__name__)

async def check_user_exist(settings: Settings, inter: disnake.Interaction) -> Optional[bool]:
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
        inventory_exist = await conn.execute_fetchall("SELECT * FROM inventory WHERE id=?", (inter.author.id,))
        bank_exist = await conn.execute_fetchall("SELECT * FROM bank WHERE id=?", (inter.author.id,))
        equipped_exist = await conn.execute_fetchall("SELECT * FROM equipped WHERE id=?", (inter.author.id,))
        arend = await conn.execute_fetchall("SELECT * FROM arend WHERE id=?", (inter.author.id,))

        if inventory_exist and bank_exist and equipped_exist and arend:
            return True
        
        if not inventory_exist:
            await conn.execute("INSERT INTO inventory (id) VALUES (?)", (inter.author.id,))
            logger.info(f"Created new user {inter.author.id} in inventory table")
        if not bank_exist:
            await conn.execute("INSERT INTO bank (id, balance) VALUES (?, 0)", (inter.author.id,))
            logger.info(f"Created new user {inter.author.id} in bank table")
        if not equipped_exist:
            await conn.execute("INSERT INTO equipped (id) VALUES (?)", (inter.author.id,))
            logger.info(f"Created new user {inter.author.id} in equipped table")
        if not arend:
            await conn.execute("INSERT INTO arend (id, balance) VALUES (?, 0)", (inter.author.id,))
            logger.info(f"Created new user {inter.author.id} in arend table")
        
        await conn.commit()
        return True
    except Exception as e:
        logger.error(f"Check user exist function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
