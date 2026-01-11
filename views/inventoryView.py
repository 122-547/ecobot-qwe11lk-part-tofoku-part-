from disnake import ButtonStyle
from disnake.ui import View, Button, Modal
import disnake
from methods.settings import Settings
from typing import List
from datetime import datetime, timedelta
from embeds.inventoryEmbed import inventory_embed
import logging
from methods.get_personal_roles import get_personal_roles
from embeds.confirmEmbed import confirm_embed
from methods.get_equipped_status import get_quipped_status
from methods.get_role_data import get_role_data
from methods.equip_role import equip_role
from methods.unequip_role import unequip_role
from methods.start_selling_role import start_selling
from methods.stop_selling_role import stop_selling
from methods.pay_arend import pay_arend
from methods.delete_role import delete_role
from embeds.confirmRemoveRoleEmbed import confirm_remove_role_embed



logger = logging.getLogger(__name__)

class InventoryView(View):
    def __init__(self,
                 user_roles: list,
                 settings: Settings,
                 current_page: int = 0,
                 
                 ):
        super().__init__(timeout=120)
        self.current_page = current_page
        self.parts = (len(user_roles)+4)//5
        self.user_roles = user_roles
        self.settings = settings

        prev_button = Button(
            label="◀️", 
            custom_id="prev",
            style=ButtonStyle.grey,
            disabled=self.current_page==0 or not user_roles,
            row=2
        )
        prev_button.callback = self.button_callback
        self.add_item(prev_button)

        for slot_idx in range(5):
            button = Button(
                label=f"🧥 {self.current_page*5+slot_idx+1}",
                custom_id=f"slot_{self.current_page*5+slot_idx+1}",
                style=ButtonStyle.grey,
                row=1,
                disabled=not user_roles or self.current_page*5+slot_idx > len(self.user_roles)-1
            )
            button.callback = self.button_callback
            self.add_item(button)
        
        next_button = Button(
            label="▶️",
            custom_id="next",
            style=ButtonStyle.grey,
            disabled=self.current_page==self.parts-1 or not user_roles,
            row=2)
        next_button.callback = self.button_callback
        self.add_item(next_button)

        my_roles = Button(
            label="⚙️ Настройки",
            custom_id="my_roles",
            style=ButtonStyle.grey,
            row=3
        )
        my_roles.callback = self.button_callback
        self.add_item(my_roles)

    
    async def button_callback(self, callback: disnake.Interaction):
        try:
            data = callback.data["custom_id"]

            if data == "prev":
                self.current_page -= 1
                embed = inventory_embed(self.user_roles)
                if not embed:
                    logger.warning("Embed is None -> return")
                    return
                view = InventoryView(self.user_roles, self.settings, self.current_page)
                await callback.response.edit_message(embed=embed, view=view)
            
            elif data == "next":
                self.current_page += 1
                embed = inventory_embed(self.user_roles)
                if not embed:
                    logger.warning("Embed is None -> return")
                    return
                view = InventoryView(self.user_roles, self.settings, self.current_page)
                await callback.response.edit_message(embed=embed, view=view)

            elif data == "my_roles":
                my_roles = await get_personal_roles(callback, self.settings)
                embed = inventory_embed(my_roles, True)
                view = MyRolesView(self.user_roles, self.settings, self.current_page, my_roles)
                await callback.response.edit_message(embed=embed, view=view)
                
            else:
                slot_num = int(data.split("_")[1])
                role_id = self.user_roles[slot_num-1]
                equipped_status = await get_quipped_status(callback, self.settings, role_id)
                if equipped_status is None:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                role = (role_id, callback.author.id, equipped_status)
                view = InventoryRoleActionMenuView(role, self.settings, self.current_page, self.user_roles)
                data = await get_role_data(role_id, self.settings)
                if not data:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                role_embed = confirm_embed(data)
                await callback.response.edit_message(embed=role_embed, view=view)

        except Exception as e:
            logger.error(f"Inventory view function error: {e}")
            return
        

class MyRolesView(View):
    def __init__(self, 
                 inv_user_roles: list,
                 settings: Settings,
                 inv_current_page: int,
                 personal_user_roles: list,
                 personal_current_page: int = 0
                 ):
        super().__init__(timeout=120)
        self.inv_current_page = inv_current_page
        self.personal_current_page = personal_current_page
        self.parts = (len(personal_user_roles)+4)//5
        self.personal_user_roles = personal_user_roles
        self.settings = settings
        self.inv_user_roles = inv_user_roles


        prev_button = Button(
            label="◀️",
            custom_id="prev",
            style=ButtonStyle.grey,
            disabled=self.personal_current_page==0 or not self.personal_user_roles,
            row=2
        )
        prev_button.callback = self.button_callback
        self.add_item(prev_button)

        for slot_idx in range(5):
            button = Button(
                label=f"🧥 {self.personal_current_page*5+slot_idx+1}",
                custom_id=f"slot_{self.personal_current_page*5+slot_idx+1}",
                style=ButtonStyle.grey,
                row=1,
                disabled=not self.personal_user_roles or self.personal_current_page*5+slot_idx > len(self.personal_user_roles)-1
            )
            button.callback = self.button_callback
            self.add_item(button)
        
        next_button = Button(
            label="▶️",
            custom_id="next",
            style=ButtonStyle.grey,
            disabled=self.personal_current_page==self.parts-1 or not self.personal_user_roles,
            row=2)
        next_button.callback = self.button_callback
        self.add_item(next_button)

        back_button = Button(
            label="🚪 Назад в инвентарь",
            custom_id="back",
            style=ButtonStyle.grey,
            row=3
        )
        back_button.callback = self.button_callback
        self.add_item(back_button)

        
        

    async def button_callback(self, callback: disnake.Interaction):
        try:
            data = callback.data["custom_id"]

            if data == "next":
                self.personal_current_page += 1
                embed = inventory_embed(self.personal_user_roles, True)
                if not embed:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                view = MyRolesView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.personal_current_page)
                if not view:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                await callback.response.edit_message(embed=embed, view=view)
                
            elif data == "prev":
                self.personal_current_page -= 1
                embed = inventory_embed(self.personal_user_roles, True)
                if not embed:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                view = MyRolesView(self.personal_user_roles, self.personal_current_page, self.inv_current_page, self.personal_user_roles, self.personal_current_page)
                if not view:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                await callback.response.edit_message(embed=embed, view=view)
            elif data == "back":
                embed = inventory_embed(self.inv_user_roles)
                view = InventoryView(self.inv_user_roles, self.settings, self.inv_current_page)
                await callback.response.edit_message(embed=embed, view=view)
            
            else:
                slot_idx = int(data.split("_")[1])
                role_id = self.personal_user_roles[slot_idx-1]
                data = await get_role_data(role_id, self.settings)
                embed = confirm_embed(data, True)
                try:
                    conn = await self.settings.get_connection()
                    
                    sh_status = bool(await conn.execute_fetchall("SELECT id FROM shop WHERE id=?", (role_id,)))
                    autopay = (await conn.execute_fetchall("SELECT autopay FROM roles WHERE id=?", (role_id,)))[0][0]
                finally:
                    await self.settings.release_connection(conn)
                view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, sh_status, autopay, role_id, self.personal_current_page)
                await callback.response.edit_message(embed=embed, view=view)



        except Exception as e:
            logger.error(f"My roles view callback function error: {e}")
            return

            


class MyRolesActionView(View):
        # выставить \ снять с продажи, включить \выключить автоплатеж, удалить роль выйти в инвентарь
        def __init__(self,
                 inv_user_roles: list,
                 settings: Settings,
                 inv_current_page: int,
                 personal_user_roles: list,
                 sh_status: bool,
                 autopay: int,
                 role_id: int,
                 personal_current_page: int = 0):
            super().__init__(timeout=120)
            self.sh_status = sh_status
            self.autopay = autopay
            self.role_id = role_id
            self.settings = settings
            self.inv_user_roles = inv_user_roles
            self.inv_current_page = inv_current_page
            self.personal_user_roles = personal_user_roles
            self.personal_current_page = personal_current_page


            start_selling = Button(
                label="🛒 Выставить",
                custom_id="start_selling",
                style=ButtonStyle.grey,
                disabled=self.sh_status,
                row=1
            )
            start_selling.callback = self.button_callback
            self.add_item(start_selling)
            stop_sellig = Button(
                label="📦 Снять",
                custom_id="stop_selling",
                style=ButtonStyle.grey,
                disabled=not self.sh_status,
                row=1
            )
            stop_sellig.callback = self.button_callback
            self.add_item(stop_sellig)

            autopay_button = Button(
                label="❌ Выключить автоплатеж" if self.autopay else "🏦 Включить автоплатеж",
                custom_id="off_autopay" if self.autopay else "on_autopay",
                style=ButtonStyle.grey,
                row=2
            )
            autopay_button.callback = self.button_callback
            self.add_item(autopay_button)

            pay_button = Button(
                label="💵 Продлить аренду",
                custom_id="pay",
                style=ButtonStyle.green,
                row=2
            )
            pay_button.callback = self.button_callback
            self.add_item(pay_button)

            delete_role = Button(
                label="🪦 Удалить роль", 
                custom_id="remove_role", 
                style=ButtonStyle.red,
                row=3
            )
            delete_role.callback = self.button_callback
            self.add_item(delete_role)

            back_button = Button(
                label="🚪 Назад в меню",
                custom_id="back",
                style=ButtonStyle.grey,
                row=4
            )
            back_button.callback = self.button_callback
            self.add_item(back_button)

        async def button_callback(self, callback: disnake.Interaction):
            try:
                data = callback.data["custom_id"]
                if data == "start_selling":
                    modal = CreateModal(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
                    await callback.response.send_modal(modal)
                elif data == "stop_selling":
                    status = await stop_selling(self.role_id, self.settings)
                    if not status:
                        await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    self.sh_status = False
                    role = await get_role_data(self.role_id, self.settings)
                    embed = confirm_embed(role)
                    view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
                    await callback.response.edit_message(embed=embed, view=view)

                elif data == "back":
                    embed = inventory_embed(self.personal_user_roles) # personal roles
                    view = MyRolesView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.personal_current_page) #...
                    await callback.response.edit_message(embed=embed, view=view)
                
                elif data == "on_autopay":
                    try:
                        conn = await self.settings.get_connection()
                        if not conn:
                            logger.warning("Connection is None -> return")
                            return
                        self.autopay = 1
                        await conn.execute("UPDATE roles SET autopay=1 WHERE id=?", (self.role_id,))
                        await conn.commit()
                        role = await get_role_data(self.role_id, self.settings)
                        embed = confirm_embed(role)
                        view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
                        await callback.response.edit_message(embed=embed, view=view)
                    except Exception as e:
                        logger.error(f"On autopay function error: {e}")
                        return
                    finally:
                        await self.settings.release_connection(conn)
                
                elif data == "off_autopay":
                    try:
                        conn = await self.settings.get_connection()
                        if not conn:
                            logger.warning("Connection is None -> return")
                            return
                        self.autopay = 0
                        await conn.execute("UPDATE roles SET autopay=0 WHERE id=?", (self.role_id,))
                        await conn.commit()
                        role = await get_role_data(self.role_id, self.settings)
                        embed = confirm_embed(role)
                        view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
                        await callback.response.edit_message(embed=embed, view=view)
                    except Exception as e:
                        logger.error(f"Off autopay function error: {e}")
                        return
                    finally:
                        await self.settings.release_connection(conn)

                elif data == "pay":
                    new_date = (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y")
                    status = await pay_arend(self.role_id, self.settings)
                    if status is None:
                        await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                        return
                    elif not status:
                        await callback.response.send_message("⚠️ У вас недостаточно средств, пополните баланс аренды...")
                    await callback.response.send_message(f"Вы оплатили аренду роли <@&{self.role_id}> до **{new_date}**")

                elif data == "remove_role":
                    role_data = await get_role_data(self.role_id, self.settings)
                    if not role_data:
                        await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                        return
                    embed = confirm_remove_role_embed(data)
                    view = ConfirmView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
                    await callback.response.send_message(embed=embed, view=view)

                    

            except Exception as e:
                logger.error(f"Personal role menu callback function error: {e}")
                return
class CreateModal(Modal):
    def __init__(self,
                 inv_user_roles: list,
                 settings: Settings,
                 inv_current_page: int,
                 personal_user_roles: list,
                 sh_status: bool,
                 autopay: int,
                 role_id: int,
                 personal_current_page: int = 0):

        self.sh_status = sh_status
        self.autopay = autopay
        self.role_id = role_id
        self.settings = settings
        self.inv_user_roles = inv_user_roles
        self.inv_current_page = inv_current_page
        self.personal_user_roles = personal_user_roles
        self.personal_current_page = personal_current_page

        # components in window
        components=[
            disnake.ui.TextInput(
                label="💰 Цена",
                placeholder="Напишите любую цену...",
                required=True,
                custom_id="price",
                max_length=16),
                
                    ]
        # activate
        super().__init__(title="🛒 Создание лота", components=components)

    # add modal callback
    async def callback(self, inter: disnake.ModalInteraction):

        price = int(inter.text_values["price"])
        status = await start_selling(self.role_id, self.settings, price)
        if not status:
            await inter.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
        self.sh_status = True
        role = await get_role_data(self.role_id, self.settings)
        embed = confirm_embed(role)
        view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
        await inter.response.edit_message(embed=embed, view=view)
        

class ConfirmView(View):
    def __init__(self,
                 inv_user_roles: list,
                 settings: Settings,
                 inv_current_page: int,
                 personal_user_roles: list,
                 sh_status: bool,
                 autopay: int,
                 role_id: int,
                 personal_current_page: int = 0):
        super().__init__(timeout=120)
        self.sh_status = sh_status
        self.autopay = autopay
        self.role_id = role_id
        self.settings = settings
        self.inv_user_roles = inv_user_roles
        self.inv_current_page = inv_current_page
        self.personal_user_roles = personal_user_roles
        self.personal_current_page = personal_current_page
    
        confirm_button = Button(
            style=ButtonStyle.red,
            custom_id="confirm",
            label="🪦 Удалить",
        )
        confirm_button.callback = self.button_callback
        self.add_item(confirm_button)

        reject_button = Button(
            style=ButtonStyle.grey,
            custom_id="reject",
            label="🚪 Назад"
        )
        reject_button.callback = self.button_callback
        self.add_item(reject_button)

    
    async def button_callback(self, callback: disnake.Interaction):
        data = callback.data["custom_id"]
        if data == "confirm":
            status = await delete_role(self.role_id, callback, self.settings)
            if not status:
                await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                return
            self.personal_user_roles.remove(self.role_id)
            embed = inventory_embed(self.personal_user_roles)
            view = MyRolesView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.personal_current_page)
            await callback.response.edit_message(embed=embed, view=view)
            await callback.send("ℹ️ Роль успешно удалена")
        
        else:
            role = await get_role_data(self.role_id, self.settings)
            embed = confirm_embed(role)
            view = MyRolesActionView(self.inv_user_roles, self.settings, self.inv_current_page, self.personal_user_roles, self.sh_status, self.autopay, self.role_id, self.personal_current_page)
            await callback.response.edit_message(embed=embed, view=view)


class InventoryRoleActionMenuView(View):
    def __init__(self, role: tuple, settings: Settings, current_page: int, user_roles: list):
        super().__init__(timeout=120)
        self.role = role
        self.role_id, self.author_id, self.eq_status = role
        self.settings = settings
        self.current_page = current_page
        self.user_roles = user_roles


        equip_button = Button(
            label="🧥 Одеть",
            custom_id="equip",
            style=ButtonStyle.green,
            row=1,
            disabled=self.eq_status
        )

        unequip_button = Button(
            label="📦 Снять",
            custom_id="unequip",
            style=ButtonStyle.red,
            row=1,
            disabled=not self.eq_status
        )
        equip_button.callback = self.button_callback
        unequip_button.callback = self.button_callback

        back_button = Button(
            label="🚪 Назад в инвентарь",
            custom_id="back",
            style=ButtonStyle.grey,
            row=2
        )
        back_button.callback = self.button_callback

        self.add_item(equip_button)
        self.add_item(unequip_button)
        self.add_item(back_button)

    async def button_callback(self, callback: disnake.Interaction):
        try:
            data = callback.data["custom_id"]

            if data == "equip":
                status = await equip_role(callback, self.settings, self.role_id)
                if not status:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                self.eq_status = True
                view = InventoryRoleActionMenuView((self.role_id, self.author_id, self.eq_status), self.settings, self.current_page, self.user_roles)
                data = await get_role_data(self.role_id, self.settings)
                embed = confirm_embed(data)
                await callback.response.edit_message(embed=embed, view=view)

            elif data == "unequip":
                status = await unequip_role(callback, self.settings, self.role_id)
                if not status:
                    await callback.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                    return
                self.eq_status = False
                view = InventoryRoleActionMenuView((self.role_id, self.author_id, self.eq_status), self.settings, self.current_page, self.user_roles)
                data = await get_role_data(self.role_id, self.settings)
                embed = confirm_embed(data)
                await callback.response.edit_message(embed=embed, view=view)


            elif data == "back":
                embed = inventory_embed(self.user_roles)
                view = InventoryView(self.user_roles, self.settings, self.current_page)
                await callback.response.edit_message(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Action menu callback function error: {e}")
            return
        
            


