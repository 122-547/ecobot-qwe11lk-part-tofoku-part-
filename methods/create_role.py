import disnake
import logging
from typing import Optional
from methods.settings import Settings
from config import Config
from embeds.arendInfoEmbed import arend_info_embed, confirm_embed
from views.createRoleView import CreateRoleConfirmView
from datetime import datetime

logger = logging.getLogger(__name__)

async def create_role(inter: disnake.Interaction, settings: Settings, color: tuple, name: str) -> Optional[bool]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        if not color:
            logger.warning("Color is None -> return")
            return
        r, g ,b = color
        color = disnake.Color.from_rgb(r, g, b)

        if not name:
            logger.warning("Name is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        
        balance = await conn.execute_fetchall("SELECT balance FROM bank WHERE id=?", (inter.author.id,))
        if not balance:
            logger.warning("Balance is None -> return")
            return
        balance = balance[0][0]
        if balance < Config.CREATION_ROLE_PRICE:
            await inter.response.send_message("У вас недостаточно средств...")
            return
        date = datetime.now().strftime("%d.%m.%Y")
        role = (name, inter.author.id, date)
        embeds = [confirm_embed(role), arend_info_embed()]
        view = CreateRoleConfirmView((name, color), settings)
        await inter.response.send_message(embeds=embeds, view=view)
        return True


    except Exception as e:
        logger.error(f"Create role function error: {e}")
        return
    finally:
        await settings.release_connection(conn)