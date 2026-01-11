import disnake
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def arend_balance_embed(balance: int) -> Optional[disnake.Embed]:
    try:
        return disnake.Embed(
            title="🏦 Баланс счета аренды",
            description=f"`{balance}$`",

        )
    except Exception as e:
        logger.error(f"Arend balance embed function error: {e}")
        return
    
