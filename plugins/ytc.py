from pyrogram import filters, Client as ace
from main import LOGGER as LOGS, prefixes
from pyrogram.types import Message
from main import Config
import os
import requests
import wget
import img2pdf
import shutil
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient

@ace.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS))
    & filters.incoming & filters.command("ytc", prefixes=prefixes)
)
async def ytc(bot: ace, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/PHOTO/{m.chat.id}"
    os.makedirs(path, exist_ok=True)
    os.makedirs(tPath, exist_ok=True)

    pages_msg = await bot.ask(m.chat.id, "Send Pages Range Eg: '1:100'\nBook Name\nBookId")
    pages, Book_Name, bid = str(pages_msg.text).split("\n")
    page = pages.split(":")
    page_1 = int(page[0])
    last_page = int(page[1]) + 1

    def down(image_link, file_name):
        wget.download(image_link, f"{tPath}/{file_name}.jpg")
        return f"{tPath}/{file_name}.jpg"

    def downloadPdf(title, imagelist):
        with open(f"{path}/{title}.pdf", "wb") as f:
            f.write(img2pdf.convert([i for i in imagelist]))
        return f"{path}/{title}.pdf"

    Show = await bot.send_message(m.chat.id, "Downloading")
    IMG_LIST = []
    for i in range(page_1, last_page):
        try:
            name = f"{str(i).zfill(3)}. page_no_{str(i)}"
            y = down(image_link=f"http://yctpublication.com/master/api/MasterController/getPdfPage?book_id={bid}&page_no={i}&user_id=14593&token=XXX",
                     file_name=name)
            IMG_LIST.append(y)
        except Exception as e:
            await m.reply_text(str(e))
            continue
    try:
        PDF = downloadPdf(title=Book_Name, imagelist=IMG_LIST)
    except Exception as e1:
        await m.reply_text(str(e1))
        PDF = None

    Thumb = "hb"
    if PDF:
        UL = Upload_to_Tg(bot=bot, m=m, file_path=PDF, name=Book_Name,
                          Thumb=Thumb, path=path, show_msg=Show, caption=Book_Name)
        await UL.upload_doc()

    shutil.rmtree(tPath, ignore_errors=True)
    shutil.rmtree(path, ignore_errors=True)
