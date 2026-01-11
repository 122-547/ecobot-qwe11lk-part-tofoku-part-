import disnake
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def remind_embed(role_name: str, rm_date: str) -> Optional[disnake.Embed]:
    try:
        if not role_name:
            logger.warning("Name is None -> return")
            return
        if not rm_date:
            logger.warning("Remove date is None -> return")
            return
        
        return disnake.Embed(
            title="Напоминание о пополнении баланса аренды",
            description=f"Пополните баланс аренды, иначе роль **{role_name}** будет удалена с сервера **EXYN** **{rm_date}**, вы можете это сделать с помощью команды **/arend_deposit**",
        )
    except Exception as e:
        logger.error(f"Remind embed function error: {e}")
