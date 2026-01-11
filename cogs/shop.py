from disnake.ext import commands
from methods.settings import Settings
import disnake
from methods.check_user_exist import check_user_exist
from methods.get_shop_roles import get_shop_roles
from methods.get_user_roles import get_user_roles
from methods.sort_role_list import order_role_list
from methods.check_slots import check_empty_slots_inventory
from embeds.pageEmbed import page_embed
from methods.create_role import create_role
from views.shopView import ShopView
from config import Config
import logging

logger = logging.getLogger(__name__)

class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.settings = Settings()
        status = await self.settings.init()
        if not status:
            logger.info("Connection pool NOT inited")
            return

        logger.info("Connection pool inited")

    @commands.slash_command(name="shop", description="Открыть магазин личных ролей", guild_ids=[Config.GUILD_ID])
    async def shop(self, inter: disnake.ApplicationCommandInteraction):
        try:
            check = await check_user_exist(self.settings, inter)
            if not check:
                logger.warning("Chech is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            shop_roles = await get_shop_roles(self.settings, inter)

            if not shop_roles:
                await inter.response.send_message("❌ Магазин пока что пуст, заглядывайте позже...")
                return

            role_list = order_role_list(shop_roles)
            user_roles = await get_user_roles(inter, self.settings)

            view = ShopView(self.settings, user_roles, role_list)

            page_list = role_list[0:5]


            parts = (len(role_list)+4)//5
            embed = page_embed(page_list, parts, 0, inter)
            if not embed:
                logger.warning("Page embed is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            await inter.response.send_message(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Shop command function error: {e}")
            return
        
    @commands.slash_command(name="create_role", description="Создайте собственную роль на сервере", guild_ids=[Config.GUILD_ID])
    async def create_role(self, inter: disnake.ApplicationCommandInteraction, name: str, r: int, g: int, b: int):
        try:
            check = await check_user_exist(self.settings, inter)
            if not check:
                logger.warning("Chech is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            check_slots = await check_empty_slots_inventory(inter, self.settings)
            if not check_slots and check_slots is not None:
                await inter.response.send_message("⚠️ У вас в инвенторе нет свободного слота...")
                return
            color = (r, g, b)
            status = await create_role(inter, self.settings, color, name)
            if not status:
                await inter.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                return
        except Exception as e:
            logger.error(f"Create role command function error: {e}")
            return
def setup(bot: commands.Bot):
    bot.add_cog(ShopCog(bot))