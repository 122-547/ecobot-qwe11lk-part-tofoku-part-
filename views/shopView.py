from disnake import ButtonStyle,  SelectOption
from embeds.pageEmbed import page_embed
from disnake.ui import View, Button, Select
import disnake
from methods.check_slots import check_empty_slots_inventory
from methods.settings import Settings
from typing import List
from embeds.confirmEmbed import confirm_embed
from methods.sort_role_list import order_role_list
from methods.buy_role import buy_role
import logging

logger = logging.getLogger(__name__)

class ShopView(View):
    def __init__(self, settings: Settings, 
                 user_roles: List[int],
                 role_list: List[tuple],
                 current_page: int = 0,
                 ):
        
        super().__init__(timeout=150)
        self.settings = settings
        self.user_roles = user_roles
        self.current_page = current_page
        self.role_list = role_list
        self.parts = (len(role_list)+4) // 5


        sort_options = [
                    SelectOption(label="📈 Сначала популярные", value="popular", description="По убыванию популярности"),
                    SelectOption(label="📉 Сначала непопулярные", value="not popular", description="По возрастанию популярности"),
                    SelectOption(label="💰 Сначала дорогие", value="expensive", description="По убыванию цены"),
                    SelectOption(label="🪙 Сначала дешевые", value="cheap", description="По возрастанию цены"),
                    SelectOption(label="🪦 Сначала старые", value="old", description="Сначала старые лоты"),
                    SelectOption(label="🕑 Сначала новые", value="new", description="Сначала новые лоты"),
                ]
        select = Select(
            placeholder="📦 Выберите сортировку...",
            options=sort_options,
            custom_id="sort_type"
        )

        select.callback = self.select_callback
        self.add_item(select)

        for i in range(1, 6):
                    label = f"🛒 {str(i)}"
                    disabled = False
                    lot_number = (self.current_page * 5) + i
                    role_idx = lot_number-1
                    if role_idx <= len(role_list)-1:
                        if self.role_list[role_idx][0] in self.user_roles:
                            label = "✅"
                            disabled = True
                    else:
                        disabled = True
                    button = Button(
                        label=label,
                        style=ButtonStyle.grey,
                        custom_id=f"lot_{lot_number}",
                        disabled=disabled
                    )
                    button.callback = self.button_callback
                    self.add_item(button)

        # scroll back button
        self.prev_button = Button(
            label="◀️",
            style=ButtonStyle.grey,
            custom_id="prev_page", 
            # disabled if page is first
            disabled=self.current_page+1 == 1
        )
        
        # scroll through button
        self.next_button = Button(
            label="▶️",
            style=ButtonStyle.grey,
            custom_id="next_page",
            # disabled if page is last
            disabled=self.current_page+1 == self.parts
        )
        # scroll buttons callback routes
        self.prev_button.callback = self.button_callback
        self.next_button.callback = self.button_callback

        # add scroll buttons
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
    
    async def button_callback(self, callback: disnake.Interaction):
            data = callback.data["custom_id"]
            if not data:
                logger.warning("Data is None -> return")
                return
            if data == "next_page":
                self.current_page += 1
                page_list = self.role_list[self.current_page*5:(self.current_page+1)*5]
                embed = page_embed(page_list, self.parts, self.current_page, callback)
                view = ShopView(self.settings, self.user_roles, self.role_list, self.current_page)
                await callback.response.edit_message(view=view, embed=embed)
            elif data == "prev_page":
                self.current_page -= 1
                page_list = self.role_list[self.current_page*5:(self.current_page+1)*5]
                embed = page_embed(page_list, self.parts, self.current_page, callback)
                view = ShopView(self.settings, self.user_roles, self.role_list, self.current_page)
                await callback.response.edit_message(view=view, embed=embed)
            else:
                check_slots = await check_empty_slots_inventory(callback, self.settings)
                if not check_slots and check_slots is not None:
                    await callback.response.send_message("⚠️ У вас в инвенторе нет свободного слота...")
                    return
                
                slot_number = int(data.split("_")[1])
                role = self.role_list[slot_number-1]
                # check balance
                try:
                    conn = await self.settings.get_connection()
                    if not conn:
                        logger.warning("Connection is None -> return")
                        return
                    balance = await conn.execute_fetchall("SELECT balance FROM bank WHERE id=?", (callback.author.id,))
                    balance = balance[0][0]
                    if balance < role[2]:
                        await callback.response.send_message("⚠️ У вас недостаточно средств...")
                        return
                except Exception as e:
                    logger.error(f"Check balance function error: {e}")
                    return
                finally:
                    await self.settings.release_connection(conn)

                page_list = self.role_list[self.current_page*5:(self.current_page+1)*5]
                embed = page_embed(page_list, self.parts, self.current_page, callback)
                conf_embed = confirm_embed(role)
                await callback.response.edit_message(embed=conf_embed, view=ConfirmView(self.settings, self.user_roles, self.role_list, self.current_page, embed, role)) # confirm view

    async def select_callback(self, callback: disnake.MessageInteraction):
        data = callback.values[0]

        self.current_page = 0
        self.role_list = order_role_list(self.role_list, data)
        if not self.role_list:
            await callback.response.send_message("⚠️ Не удалось, попробуйте позже...")
            return
        page_list = self.role_list[self.current_page*5:(self.current_page+1)*5]
        embed = page_embed(page_list, self.parts, self.current_page, callback)
        view = ShopView(self.settings, self.user_roles, self.role_list, self.current_page)
        await callback.response.edit_message(embed=embed, view=view)


class ConfirmView(View):
    def __init__(self,
                 settings: Settings,
                 user_roles: list,
                 role_list: List[tuple],
                 current_page: int,
                 embed: disnake.Embed,
                 role: tuple):
        super().__init__(timeout=120)
        self.settings = settings
        self.user_roles = user_roles
        self.role_list = role_list
        self.current_page = current_page
        self.embed = embed
        self.role = role
    
        confirm_button = Button(
            style=ButtonStyle.green,
            custom_id="confirm",
            label="✅ Купить",
        )
        confirm_button.callback = self.button_callback
        self.add_item(confirm_button)

        reject_button = Button(
            style=ButtonStyle.grey,
            custom_id="reject",
            label="❌ Назад"
        )
        reject_button.callback = self.button_callback
        self.add_item(reject_button)

    
    async def button_callback(self, callback: disnake.Interaction):
        # await callback.response.defer()
        data = callback.data["custom_id"]
        if data == "confirm":
            status = await buy_role(self.role, self.settings, callback)
            if status:
                embed = confirm_embed(self.role)
                embed.color = disnake.Color.green()
                embed.add_field("Статус:", value="✅ Куплена")
                await callback.response.edit_message(embed=embed, view=None)
                await callback.send(f"🎒 Роль <@&{self.role[0]}> уже ждет вас в инвентаре! **__/inv__**")
        
        else:
            embed = self.embed
            view = ShopView(self.settings, self.user_roles, self.role_list, self.current_page)
            await callback.response.edit_message(embed=embed, view=view)