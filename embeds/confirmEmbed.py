import disnake
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def confirm_embed(role: tuple, personal: bool = False) -> Optional[disnake.Embed]:
    try:
        title = "ℹ️ О личной роли"
        if personal:
            title = "⚙️ Настройка роли"
        if not role:
            logger.warning("Role is None -> return")
            return
        role_id, author_id, price, count, date = role
        if price is None:
            price = "Не назначена"
        return disnake.Embed(
            title=title,
            description=
            f"・Роль: <@&{role_id}>\n"
            f"・Продавец: <@{author_id}>\n"
            f"・Цена: **{price}**\n"
            f"・Покупок: **{count}**\n"
            f"・Создана: **{date}**\n",
        )
    except Exception as e:
        logger.error(f"Confirm embed function error: {e}")
        return
    