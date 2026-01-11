import disnake
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def confirm_embed(role: tuple, personal: bool = False) -> Optional[disnake.Embed]:
    try:
        title = "ℹ️ О личной роли"
        
        if not role:
            logger.warning("Role is None -> return")
            return
        role_name = role[0]
        author_id = role[1]
        date = role[2]
        return disnake.Embed(
            title=title,
            description=
            f"・Название: **{role_name}**\n"
            f"・Владелец: <@{author_id}>\n"
            f"・Создана: **{date}**\n",
        )
    except Exception as e:
        logger.error(f"Confirm embed function error: {e}")
        return
    
def arend_info_embed() -> Optional[disnake.Embed]:
    try:
        return disnake.Embed(
            title="⚠️ Об условиях аренды слота",
            description="""
Нажимая кнопку **"Создать"**, вы соглашаетесь с условиями аренды слота личной роли на сервере **EXYN**.

**Условия:**
・Создавая роль, вы даете роли срок жизни длиной в 1 месяц (30дн).
・Если баланс аренды не будет вовремя пополнен, то роль удаляется с сервера.
・При нехватке средств на балансе аренды, бот напомнит вам о пополнении за 2 дня до истечения срока жизни роли.
・Пополнить баланс аренды вы можете с помощью комманды **/arend_deposit**
・При истечении срока жизни роли, при наличии средств, с баланса списывается плата за аренду на следующий месяц (30дн).
・Вы можете отключить функцию автоплатежа в настройках личной роли **/inv** -> Мои роли
""",

        )
    except Exception as e:
        logger.error(f"Arend info embed function error: {e}")
        return
    