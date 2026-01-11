import os
import disnake
from disnake.ext import commands
from methods.settings import Settings
from config import Config
import logging
import logging.handlers

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="/", intents=intents)

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, "bot.log")


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.handlers.TimedRotatingFileHandler(
    log_filename, 
    when="midnight", 
    interval=1, 
    backupCount=10,
    encoding='utf-8'
)

handler.suffix = "%Y-%m-%d.log" 
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)


@bot.event
async def on_ready():

    try:
        print(f"{bot.user.name} bot is ready!")
        logger.info("Bot is ready!")
    except Exception as e:
        logger.error(f"On ready function error: {e}")

@bot.command()
async def load(ctx, extension):
    if ctx.author.id == 991073188861599744:
        bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} was loaded.")
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.command()
async def unload(ctx, extension):

    if ctx.author.id == 991073188861599744:
        bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} was unloaded.")
    else:
        await ctx.send("You are not authorized to use this command.")

try:
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")
    logger.info("Cogs loaded!")
except Exception as e:
    logger.error(f"Loading extensions error: {e}")



if __name__ == '__main__':
    bot.run(Config.TOKEN)
