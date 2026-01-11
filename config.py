from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TOKEN = os.getenv("TOKEN")
    CREATION_ROLE_PRICE = int(os.getenv("CREATION_ROLE_PRICE"))
    AREND_SLOT_PRICE = int(os.getenv("AREND_SLOT_PRICE"))
    GUILD_ID = int(os.getenv("GUILD_ID"))
