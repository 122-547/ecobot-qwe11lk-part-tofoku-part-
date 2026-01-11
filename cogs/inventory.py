"""
инвентарь с крутящимися слотами
получить роли юзера
составить ембед
сделать кутящуюся вьюшку

купленные роли - одеть, снять, в меню
созданные роли - выставить, скрыть, удалить, убрать автоплатеж, в меню
удалить - вьюшка подтверждения

"""
import disnake
from disnake.ext import commands
import logging
from typing import Optional
from config import Config
from methods.settings import Settings
from methods.get_user_roles import get_user_roles
from embeds.inventoryEmbed import inventory_embed
from views.inventoryView import InventoryView
from methods.check_user_exist import check_user_exist

logger = logging.getLogger(__name__)

class InventoryCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.settings = Settings()
        await self.settings.init()
    
    @commands.slash_command(name="inv", description="Открыть инвентарь", guild_ids=[Config.GUILD_ID])
    async def inventory(self, inter: disnake.ApplicationCommandInteraction):
        try:
            check = await check_user_exist(self.settings, inter)
            if not check:
                logger.warning("Chech is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            user_roles = await get_user_roles(inter, self.settings)
            embed = inventory_embed(user_roles)
            if not embed:
                logger.warning("Embed is None -> return")
                return
            view = InventoryView(user_roles, self.settings)
            await inter.response.send_message(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Inventory command function error: {e}")
            return


def setup(bot: commands.Bot):
    bot.add_cog(InventoryCog(bot))