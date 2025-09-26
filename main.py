import os
import threading
import asyncio
import logging

from flask import Flask
from pyrogram import Client as AFK, idle
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram import enums
from pyrogram.types import ChatMember
import tgcrypto
from pyromod import listen
from tglogging import TelegramLogHandler

# Config
class Config(object):
    BOT_TOKEN = "8496276598:AAEHwjuuBq5MrRzKpOE7zqzfZcxq_IVBSPo"   # तुम्हारा टोकन
    API_ID = 17640565                                                # तुम्हारा API_ID
    API_HASH = "ff67816c19a48aff1f86204ff61ce786"                    # तुम्हारा API_HASH
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    SESSIONS = "./SESSIONS"

    AUTH_USERS = [7959404410]  # authorised users
    GROUPS = [-1002806996269]  # groups
    LOG_CH = "-1003166167318"  # log channel

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        TelegramLogHandler(
            token=Config.BOT_TOKEN,
            log_chat_id=Config.LOG_CH,
            update_interval=2,
            minimum_lines=1,
            pending_logs=200000
        ),
        logging.StreamHandler()
    ]
)

LOGGER = logging.getLogger(__name__)
LOGGER.info("live log streaming to telegram.")

# Flask app
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# Pyrogram client
plugins = dict(root="plugins")
PRO = AFK(
    "AFK-DL",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=120,
    plugins=plugins,
    workdir=Config.SESSIONS,
    workers=2,
)

# prepare chat list
chat_id = Config.GROUPS + Config.AUTH_USERS

async def main():
    await PRO.start()
    bot_info = await PRO.get_me()
    LOGGER.info(f"<--- @{bot_info.username} Started --->")

    for i in chat_id:
        try:
            await PRO.send_message(chat_id=i, text="Bot Started! ♾ /pro ")
        except Exception as d:
            LOGGER.warning(d)
            continue

    await idle()
    await PRO.stop()

if __name__ == "__main__":
    # ensure directories exist
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    os.makedirs(Config.SESSIONS, exist_ok=True)

    # start flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # run the async main loop
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("Shutting down...")
    finally:
        LOGGER.info("<---Bot Stopped--->")
