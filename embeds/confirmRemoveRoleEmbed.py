import disnake
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def confirm_remove_role_embed(data: tuple) -> Optional[disnake.Embed]:
    try:
        if not data:
            logger.warning("Data is None -> return")
            return
        role_id, author_id, price, count, date = data
        return disnake.Embed(
            title="⚠️ Удаление роли",
            description=
            f"・Роль: <@&{role_id}>\n"
            f"・Продавец: <@{author_id}>\n"
            f"・Цена: **{price}**\n"
            f"・Покупок: **{count}**\n"
            f"・Создана: **{date}**\n\n"
            f'ℹ️ Подтвердите удаление роли, нажав на кнопку **"Удалить"**'
        )
    except Exception as e:
        logger.error(f"Confirm remove role embed function error: {e}")
        return