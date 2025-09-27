# plugins/drm.py
from pyrogram import filters, Client
from pyrogram.types import Message
from main import LOGGER, prefixes, Config
import os
import shutil
import shlex
from handlers.uploader import Upload_to_Tg
from handlers.tg import TgClient

@Client.on_message(
    (filters.chat(Config.GROUPS) | filters.chat(Config.AUTH_USERS)) &
    filters.incoming & filters.command("drm", prefixes=prefixes)
)
async def drm(client: Client, m: Message):
    path = f"{Config.DOWNLOAD_LOCATION}/{m.chat.id}"
    tPath = f"{Config.DOWNLOAD_LOCATION}/THUMB/{m.chat.id}"
    os.makedirs(path, exist_ok=True)

    # ask input
    inputData = await client.ask(m.chat.id, "Send (4 lines):\nMPD\nNAME\nQUALITY\nCAPTION")
    if not inputData or not getattr(inputData, "text", ""):
        await m.reply_text("No input received.")
        return
    parts = inputData.text.strip().split("\n")
    if len(parts) < 4:
        await m.reply_text("❌ Please send exactly 4 lines:\nMPD\nNAME\nQUALITY\nCAPTION")
        return
    mpd, raw_name, Q, CP = parts[:4]
    try:
        Q_int = int(Q)
    except:
        await m.reply_text("Quality should be a number like 360, 720, 1080.")
        return
    name_safe = f"{TgClient.parse_name(raw_name)} ({Q_int}p)"
    LOGGER.info("DRM download request: %s", name_safe)

    # keys
    inputKeys = await client.ask(m.chat.id, "Send Kid:Key (one per line)")
    if not inputKeys or not getattr(inputKeys, "text", ""):
        await m.reply_text("No keys provided.")
        return
    keys_data = [k.strip() for k in inputKeys.text.strip().split("\n") if k.strip()]
    if not keys_data:
        await m.reply_text("No keys provided.")
        return
    # build keys string for mp4decrypt: "kid:key kid2:key2"
    keys_param = " ".join(shlex.quote(k) for k in keys_data)

    BOT = TgClient(client, m, path)
    Thumb = await BOT.thumb()
    prog = await client.send_message(m.chat.id, f"Downloading DRM Video: {name_safe}", disable_web_page_preview=True)

    # run yt-dlp to download fragments
    cmd1 = f'yt-dlp -o "{path}/fileName.%(ext)s" -f "bestvideo[height<={Q_int}]+bestaudio" --allow-unplayable-format --external-downloader aria2c "{mpd}"'
    try:
        rc = os.system(cmd1)
        if rc != 0:
            raise RuntimeError("yt-dlp failed (rc=%s)" % rc)
    except Exception as e:
        try: await prog.delete(True)
        except: pass
        await m.reply_text(f"Download failed: {e}")
        return

    # decrypt + merge
    try:
        files = os.listdir(path)
        for data in files:
            lower = data.lower()
            if lower.endswith(".mp4") and "fileName" in lower:
                in_video = os.path.join(path, data)
                # decrypt to standard name
                cmd2 = f'mp4decrypt {keys_param} --show-progress {shlex.quote(in_video)} {shlex.quote(os.path.join(path,"video.mp4"))}'
                if os.system(cmd2) != 0:
                    raise RuntimeError("mp4decrypt (video) failed")
                os.remove(in_video)
            elif lower.endswith(".m4a") and "fileName" in lower:
                in_audio = os.path.join(path, data)
                cmd3 = f'mp4decrypt {keys_param} --show-progress {shlex.quote(in_audio)} {shlex.quote(os.path.join(path,"audio.m4a"))}'
                if os.system(cmd3) != 0:
                    raise RuntimeError("mp4decrypt (audio) failed")
                os.remove(in_audio)

        # merge
        video_in = os.path.join(path, "video.mp4")
        audio_in = os.path.join(path, "audio.m4a")
        out_file = os.path.join(path, f"{name_safe}.mp4")
        if not (os.path.exists(video_in) and os.path.exists(audio_in)):
            raise RuntimeError("Decrypted audio/video not found")

        cmd4 = f'ffmpeg -y -i {shlex.quote(video_in)} -i {shlex.quote(audio_in)} -c copy {shlex.quote(out_file)}'
        if os.system(cmd4) != 0:
            raise RuntimeError("ffmpeg merge failed")

        # cleanup temp decrypted files
        try:
            os.remove(video_in)
            os.remove(audio_in)
        except:
            pass
            cc = f"{name_safe}.mp4\n\nDescription:-\n{CP}"
        UL = Upload_to_Tg(bot=client, m=m, file_path=out_file, name=name_safe,
                          Thumb=Thumb, path=path, show_msg=prog, caption=cc)
        await UL.upload_video()
    except Exception as e:
        try: await prog.delete(True)
        except: pass
        await m.reply_text(f"Error processing file:\n{e}")
    finally:
        # safe cleanup
        try:
            if os.path.exists(tPath):
                shutil.rmtree(tPath)
        except:
            pass
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
        except:
            pass
        try:
            await m.reply_text("Done")
        except:
            pass
