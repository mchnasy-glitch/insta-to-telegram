import os
import time
import re
import sqlite3
import instaloader
from telegram import Bot, InputMediaPhoto, InputMediaVideo
import asyncio

# ================== تنظیمات شما ==================
TELEGRAM_BOT_TOKEN = "8550951200:AAH0waHPBa-aXrT5wY7xOXjrBAAXiz-pS7c"
TELEGRAM_CHANNEL_ID = "@papoosh_charm"
INSTAGRAM_TARGET_USERNAME = "alacharm_meraj"
CHECK_INTERVAL_SECONDS = 900  # بررسی هر ۱۵ دقیقه

# متنی که پایین پست‌های کانال شما اضافه می‌شود:
MY_FOOTER_SIGNATURE = """
👠 کفش چرم طبیعی اعلا
🛍 جهت سفارش و اطلاعات بیشتر به آیدی زیر پیام دهید:
🆔 @mch_nsy
📢 کانال ما:
papoosh_charm@
"""
# =================================================

def init_db():
    conn = sqlite3.connect("posted_cache.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            post_shortcode TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_already_posted(shortcode: str) -> bool:
    conn = sqlite3.connect("posted_cache.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM posted WHERE post_shortcode = ?", (shortcode,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_as_posted(shortcode: str):
    conn = sqlite3.connect("posted_cache.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO posted (post_shortcode) VALUES (?)", (shortcode,))
    conn.commit()
    conn.close()

def clean_and_customize_caption(caption: str) -> str:
    if not caption:
        caption = ""
    # پاکسازی شماره‌های تماس منبع
    cleaned = re.sub(r'(\+?98|0)?9\d{9}', '', caption)
    # پاکسازی آیدی‌های متفرقه
    cleaned = re.sub(r'@\w+', '', cleaned)
    # ترکیب با امضای کانال شما
    final_caption = f"{cleaned.strip()}\n\n{MY_FOOTER_SIGNATURE.strip()}"
    return final_caption[:1020]

async def process_and_send():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_history=False
    )

    print(f"[*] بررسی پیج: {INSTAGRAM_TARGET_USERNAME}...")
    try:
        profile = instaloader.Profile.from_username(L.context, INSTAGRAM_TARGET_USERNAME)
        posts = profile.get_posts()

        for post in list(posts)[:3]:
            shortcode = post.shortcode
            if is_already_posted(shortcode):
                continue

            print(f"[+] ارسال پست جدید: {shortcode}")
            caption = clean_and_customize_caption(post.caption)

            if not post.is_sidecar:
                if post.is_video:
                    await bot.send_video(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        video=post.video_url,
                        caption=caption
                    )
                else:
                    await bot.send_photo(
                        chat_id=TELEGRAM_CHANNEL_ID,
                        photo=post.url,
                        caption=caption
                    )
            else:
                media_group = []
                nodes = list(post.get_sidecar_nodes())
                for idx, node in enumerate(nodes):
                    curr_caption = caption if idx == 0 else None
                    if node.is_video:
                        media_group.append(InputMediaVideo(media=node.video_url, caption=curr_caption))
                    else:
                        media_group.append(InputMediaPhoto(media=node.display_url, caption=curr_caption))
                
                if media_group:
                    await bot.send_media_group(chat_id=TELEGRAM_CHANNEL_ID, media=media_group)

            mark_as_posted(shortcode)
            print(f"[✓] پست {shortcode} با موفقیت در کانال منتشر شد.")
            await asyncio.sleep(5)

    except Exception as e:
        print(f"[!] خطا: {e}")async def main():    init_db()
    while True:
        await process_and_send()
        print(f"[*] استراحت به مدت {CHECK_INTERVAL_SECONDS} ثانیه...")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if name == "main":
    asyncio.run(main())
