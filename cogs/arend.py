import disnake
from disnake.ext import commands, tasks
from datetime import time
from config import Config
import logging
from methods.settings import Settings
from methods.check_arend_balance import get_arend_balance
from embeds.arendBalanceEmbed import arend_balance_embed
from methods.arend_deposit import arend_deposit
from methods.check_role_remove import check_role_remove
from methods.check_user_exist import check_user_exist

logger = logging.getLogger(__name__)

class ArendCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.settings = Settings(pool_size=5)
        await self.settings.init()
        
    @commands.slash_command(name="arend_balance", description="Посмотреть баланс аренды", guild_ids=[Config.GUILD_ID])
    async def arend_balance(self, inter: disnake.ApplicationCommandInteraction):
        try:
            check = await check_user_exist(self.settings, inter)
            if not check:
                logger.warning("Chech is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            balance = await get_arend_balance(inter, self.settings)
            embed = arend_balance_embed(balance)
            await inter.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Arend balance command function error: {e}")
            return
    
    @commands.slash_command(name="arend_deposit", description="Пополнить баланс аренды", guild_ids=[Config.GUILD_ID])
    async def arend_deposit(self, inter: disnake.ApplicationCommandInteraction, deposit: int):
        try:
            check = await check_user_exist(self.settings, inter)
            if not check:
                logger.warning("Chech is None -> return")
                await inter.response.send_message("⚠️ Не удалось, попробуйте позже...")
                return
            status = await arend_deposit(inter, self.settings, deposit)
            if status == "no-money":
                await inter.response.send_message("⚠️ У вас недостаточно средств")
                return
            elif not status:
                await inter.response.send_message("⚠️ Что-то пошло не так, попробуйте позже...")
                return
            await inter.response.send_message("ℹ️ Баланс аренды успешно пополнен!")
        except Exception as e:
            logger.error(f"Arend deposit command function error: {e}")
            return
    
    @tasks.loop(time=time(hour=1))
    async def check_role_remove(self):
        status = await check_role_remove(self.settings, self.bot)
        if not status:
            logger.error("Check role function was wrong")
            return
        

def setup(bot: commands.Bot):
    bot.add_cog(ArendCog(bot))
