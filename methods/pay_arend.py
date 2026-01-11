from methods.settings import Settings
from typing import Optional
from methods.get_role_data import get_role_data
from datetime import datetime, timedelta
import logging
from config import Config

logger = logging.getLogger(__name__)

async def pay_arend(role_id: int, settings: Settings) -> Optional[bool]:
    try:
        if not role_id:
            logger.warning("Role id is None -> return")
            return
        data = await get_role_data(role_id, settings)
        if not data:
            logger.warning("Data is None -> return")
            return

        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        balance = await conn.execute_fetchall("SELECT balance FROM arend WHERE id=?", (data[1],))
        balance = balance[0][0]
        if balance < Config.AREND_SLOT_PRICE:
            return False
        new_date = (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y")
        query = f"UPDATE arend SET balance=balance-{Config.AREND_SLOT_PRICE} WHERE id=?"
        await conn.execute(query, (data[1],))
        await conn.execute("UPDATE roles SET remove_date=? WHERE id=?", (new_date, role_id))
        await conn.commit()
        return True
        
        
    except Exception as e:
        logger.error(f"Pay arend function error: {e}")
        return
    finally:
        await settings.release_connection(conn)