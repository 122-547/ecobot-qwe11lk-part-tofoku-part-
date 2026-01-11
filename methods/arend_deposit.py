import disnake
from typing import Optional, Any
import logging
from methods.settings import Settings

logger = logging.getLogger(__name__)

async def arend_deposit(inter: disnake.Interaction, settings: Settings, deposit: int) -> Optional[Any]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        if not deposit:
            logger.warning("Deposit is None -> return")
            return
        
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        
        balance = await conn.execute_fetchall("SELECT balance FROM bank WHERE id=?", (inter.author.id,))
        if balance[0][0] < deposit:
            return "no-money"
        
        query = f"UPDATE bank SET balance=balance-{deposit} WHERE id=?"
        await conn.execute(query, (inter.author.id,))

        query = f"UPDATE arend SET balance=balance+{deposit} WHERE id=?"
        await conn.execute(query, (inter.author.id,))

        await conn.commit()

        return True
    except Exception as e:
        logger.error(f"Arend deposit function error: {e}")
        return
    finally:
        await settings.release_connection(conn)

        
