import os
import threading
import logging

from flask import Flask
from pyrogram import Client as AFK, idle
from tglogging import TelegramLogHandler

# ---------------- Config ----------------
class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8496276598:AAEHwjuuBq5MrRzKpOE7zqzfZcxq_IVBSPo")
    API_ID = int(os.environ.get("API_ID", "17640565"))
    API_HASH = os.environ.get("API_HASH", "ff67816c19a48aff1f86204ff61ce786")
    DOWNLOAD_LOCATION = "./DOWNLOADS"
    SESSIONS = "./SESSIONS"

    AUTH_USERS = os.environ.get('AUTH_USERS', '7959404410').split(',')
    AUTH_USERS = [int(i) for i in AUTH_USERS]

    GROUPS = os.environ.get('GROUPS', '-1002806996269').split(',')
    GROUPS = [int(i) for i in GROUPS]

    LOG_CH = os.environ.get("LOG_CH", "-1003166167318")


# ---------------- Logging ----------------
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

LOGGER = logging.getLogger(name)
LOGGER.info("Live log streaming to telegram.")

# ---------------- Flask ----------------
flask_app = Flask(name)

@flask_app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host="0.0.0.0", port=port)

# ---------------- Main ----------------
if name == "main":
    # Ensure directories exist
    if not os.path.isdir(Config.DOWNLOAD_LOCATION):
        os.makedirs(Config.DOWNLOAD_LOCATION)
    if not os.path.isdir(Config.SESSIONS):
        os.makedirs(Config.SESSIONS)

    # Pyrogram client
    PRO = AFK(
        "AFK-DL",
        bot_token=Config.BOT_TOKEN,
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        sleep_threshold=120,
        workdir=f"{Config.SESSIONS}/",
        workers=2,
        plugins=dict(root="plugins")
    )

    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()

    # Start bot
    PRO.start()
    bot_info = PRO.get_me()
    LOGGER.info(f"<--- @{bot_info.username} Started --->")

    # Send start message
    for i in Config.AUTH_USERS + Config.GROUPS:
        try:
            PRO.send_message(chat_id=i, text="Bot Started! ♾ /pro ")
        except Exception as d:
            print(d)

    # Keep alive
    idle()

    PRO.stop()
    LOGGER.info("<--- Bot Stopped --->")
