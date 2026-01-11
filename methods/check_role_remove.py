import disnake
from typing import Optional
import logging
from disnake.ext import commands
from methods.settings import Settings
from datetime import datetime, timedelta
from config import Config
from embeds.reminedEmbed import remind_embed

logger = logging.getLogger(__name__)

async def check_role_remove(settings: Settings, bot: commands.Bot) -> Optional[bool]:
    try:
        if not settings:
            logger.warning("Settings is None -> return")
            return
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        now = datetime.now()
        nt_date = (now + timedelta(days=2)).strftime("%d.%m.%Y")
        rm_date = now.strftime("%d.%m.%Y")

        rem_roles = await conn.execute_fetchall("SELECT id, author_id, autopay FROM roles WHERE remove_date=?", (rm_date,))
        if not rem_roles:
            logger.warning("Remove roles is None -> return")
            return
        not_roles = await conn.execute_fetchall("SELECT id, author_id FROM roles WHERE remove_date=?", (nt_date,))
        if not not_roles:
            logger.warning("Notify roles is None -> return")
            return
        
        for role in not_roles:
            balance = await conn.execute_fetchall("SELECT balance FROM arend WHERE id=?", (role[1],))
            if not balance:
                logger.warning("Balance is None")
                continue
            balance = [0][0]
            if balance < Config.AREND_SLOT_PRICE:
                await notify_user(role[1], role[0], bot, nt_date)
                
            
        for role in rem_roles:
            status = await pay(role[0], role[1], role[2], settings)
            if not status and status is not None:
                await delete_role(role[1], role[0], bot, settings)
            elif not status and status is None:
                logger.warning("Payment status is None")

        return True
        

    except Exception as e:
        logger.error(f"Check role remove function error: {e}")
        return
    finally:
        await settings.release_connection(conn)

async def notify_user(user_id: int, role_id: int, bot: commands.Bot, rm_date: str) -> Optional[bool]:
    try:
        user = bot.get_user(user_id)
        if not user:
            logger.warning("User is None -> return")
            return
        guild = bot.get_guild(int(Config.GUILD_ID))
        if not guild:
            logger.warning("Guild is None -> return")
            return
        role = guild.get_role(role_id)
        if not role:
            logger.warning("Role is None -> return")
            return
        name = role.name
        embed = remind_embed(name, rm_date)
        if not embed:
            logger.warning("Embed is None -> return")
            return
        await user.send(embed=embed)
    except Exception as e:
        logger.error(f"Notify user function error: {e}")
        return
    
async def delete_role(user_id: int, role_id: int, bot: commands.Bot, settings: Settings) -> Optional[bool]:
    try:
        user = bot.get_user(user_id)
        if not user:
            logger.warning("User is None -> return")
            return
        guild = bot.get_guild(int(Config.GUILD_ID))
        if not guild:
            logger.warning("Guild is None -> return")
            return
        role = guild.get_role(role_id)
        if not role:
            logger.warning("Role is None -> return")
            return
        name = role.name
        await role.delete()
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        await conn.execute("DELETE FROM roles WHERE id=?", (role_id,))
        await conn.execute("DELETE FROM shop WHERE id=?", (role_id,))
        conditions = [f'"{i}"={role_id}' for i in range(1, 21)]
        query = f'SELECT * FROM inventory WHERE {" OR ".join(conditions)}'
        inventory = await conn.execute_fetchall(query)
        if not inventory:
            logger.warning("Inventory is None -> return")
            return
        for user in inventory:
            user_inv = user[1:]
            slot = user_inv.index(role_id)+1
            query = f"UPDATE inventory SET [{str(slot)}]=NULL WHERE id=?"
            await conn.execute(query, (user[0],))
        query = f'SELECT * FROM equipped WHERE {" OR ".join(conditions)}'
        equipped = await conn.execute_fetchall(query)
        if not equipped:
            logger.warning("Equipped is None -> return")
            return
        for user in equipped:
            user_eq = user[1:]
            slot = user_eq.index(role_id)+1
            query = f"UPDATE inventory SET [{str(slot)}]=NULL WHERE id=?"
            await conn.execute(query, (user[0],))
        
        await conn.commit()
        await user.send(f"Ваша роль {name} была удалена с сервера **EXYN** за неуплату аренды.")
        return True

    except Exception as e:
        logger.error(f"Delete role function error: {e}")
        return
    finally:
        await settings.release_connection(conn)

async def pay(role_id: int, author_id: int, autopay: int, settings: Settings) -> Optional[bool]:
    try:
        if not role_id:
            logger.warning("Role id is None -> return")
            return
        if not author_id:
            logger.warning("Author id is None -> return")
            return
        if not settings:
            logger.warning("Settings is None -> return")
            return
        
        if not autopay:
            return False
        
        conn = await settings.get_connection()
        if not conn:
            logger.warning("Connection is None -> return")
            return
        query = f"UPDATE arend SET balance=balance-{Config.AREND_SLOT_PRICE} WHERE id=?"
        await conn.execute(query, (author_id,))
        new_date = (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y")
        await conn.execute("UPDATE roles SET remove_date=? WHERE id=?", (new_date, role_id))
        await conn.commit()
        return True
    
    except Exception as e:
        logger.error(f"Payment function error: {e}")
        return
    finally:
        await settings.release_connection(conn)
