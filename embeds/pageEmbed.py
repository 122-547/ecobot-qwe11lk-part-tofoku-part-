import disnake
import logging

logger = logging.getLogger(__name__)

def page_embed(page_list, page_count, page_number, inter: disnake.Interaction):
    if not page_list:
        embed = disnake.Embed(
            title="🛍️ **Магазин личных ролей**",
            description="❌ Упс... Полки магазина пока что пусты...",
        )
        return embed
    
    role_descriptions = []
    
    for i, role in enumerate(page_list, start=1):
        try:
            role_id = role[0] if len(role) > 0 else 0
            author_id = role[1] if len(role) > 1 else 0
            role_price = role[2] if len(role) > 2 else 0
            role_date = role[4] if len(role) > 4 else "Неизвестно"
            role_count = role[3] if len(role) > 3 else 0
            if role_price is None:
                role_price = "Не указана"
            role_description = f"""**{i})** Роль: <@&{role_id}>
・Продавец: <@{author_id}>
・Цена: **{role_price}**
・Покупок: **{role_count}**
・Создана: **{role_date}**
"""
            role_descriptions.append(role_description)
        except Exception as e:
            role_descriptions.append(f"**{i})** Ошибка загрузки роли")
    

    embed = disnake.Embed(
        title="🛍️ **Магазин личных ролей**",
        description="\n".join(role_descriptions),
    )
    
    embed.set_footer(text=f"Страница {page_number+1} из {page_count}")
    
    if hasattr(inter, 'author') and inter.author and inter.author.avatar:
        embed.set_thumbnail(url=inter.author.avatar.url)
    
    return embed