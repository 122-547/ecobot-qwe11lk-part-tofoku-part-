import disnake
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def inventory_embed(user_roles: list, personal: bool = False) -> Optional[disnake.Embed]:
    try:
        title = "🎒 Ваш инвентарь"
        if personal:
            title = "⚙️ Настройка ролей"

        if not user_roles:
            return disnake.Embed(
                title=title,
                description="❌ Пока что тут пусто, загляните в магазин! **__/shop__**" if not personal else "❌ Пока что тут пусто, создайте свою роль! **__/create_role__**",
            )
        parts = (len(user_roles)+4)//5

        embed = disnake.Embed(
            title=title,
        )
        for i in range(0, parts):
            page_list = []
            for e in range(5):
                slot_num = e+1
                role_id = user_roles[i*5+e]
                page_list.append(f"{i*5+slot_num}) <@&{role_id}>"),
                if i*5+e == len(user_roles)-1:
                    break

            embed.add_field(
                name=f"{i+1} страница",
                value="\n".join(page_list),
                inline=True
            )
        

        return embed
    except Exception as e:
        logger.error(f"Inventory embed function error: {e}")
        return