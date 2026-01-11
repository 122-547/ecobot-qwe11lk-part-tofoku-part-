from disnake import ButtonStyle
from disnake.ui import View, Button
import disnake
from methods.settings import Settings
from datetime import timedelta, datetime
from config import Config
import logging


logger = logging.getLogger(__name__)

class CreateRoleConfirmView(View):
    def __init__(self, role: tuple, settings: Settings):
        super().__init__(timeout=120)
        self.name, self.color = role
        self.settings = settings

        confirm_button = Button(
            label="✅ Создать", 
            custom_id="confirm",
            style=ButtonStyle.green
        )
        confirm_button.callback = self.button_callback
        self.add_item(confirm_button)

        reject_button = Button(
            label="🚪 Назад",
            custom_id="reject",
            style=ButtonStyle.grey
        )
        reject_button.callback = self.button_callback
        self.add_item(reject_button)


    async def button_callback(self, callback: disnake.Interaction):
        try:
            data = callback.data["custom_id"]
            
            if data == "confirm":
                try:
                    role = await callback.guild.create_role(name=self.name, color=self.color)
                    if not role:
                        await callback.response.send_message("⚠️ Что то пошло не так, повторите попытку позже...")
                        return
                    conn = await self.settings.get_connection()
                    if not conn:
                        logger.warning("Connection is None -> return")
                        return
                    role_id = role.id
                    author_id = callback.author.id
                    now = datetime.now()
                    creation_date = now.strftime("%d.%m.%Y")
                    remove_date = (now + timedelta(days=30)).strftime("%d.%m.%Y")
                    await conn.execute("INSERT INTO roles (id, author_id, price, count, creation_date, remove_date, autopay) VALUES (?, ?, NULL, 1, ?, ?, 1)", (role_id, author_id, creation_date, remove_date))
                    slots = await conn.execute_fetchall("SELECT * FROM inventory WHERE id=?", (callback.author.id,)) # [(int), (int), (None), (...)]
                    slots = slots[0][1:]
                    empty_slot = slots.index(None)
                    query = f"UPDATE inventory SET [{str(empty_slot+1)}]=? WHERE id=?"
                    await conn.execute(query, (role_id, callback.author.id))
                    query = f"UPDATE bank SET balance=balance-{Config.CREATION_ROLE_PRICE} WHERE id=?"
                    await conn.execute(query, (callback.author.id,))
                    await conn.commit()
                    await callback.response.edit_message("🎒 Ваша новая роль уже ждет вас в инвенторе! **__/inv__**", embed=None, view=None)

                except Exception as e:
                    logger.error(f"Creation role function error: {e}")
                    return
                finally:
                    await self.settings.release_connection(conn)
            else:
                await callback.delete_original_response()
        
        except Exception as e:
            logger.error(f"Callback creation function error: {e}")
            return
        