import os
import re
import sqlite3
import asyncio
import instaloader
from telegram import Bot, InputMediaPhoto, InputMediaVideo
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = "@papoosh_charm
"
INSTAGRAM_TARGET_USERNAME = "alacharm_meraj"
CHECK_INTERVAL_SECONDS = 900

MY_FOOTER_SIGNATURE = """
👠 کفش چرم طبیعی اعلا
🛍 جهت سفارش و اطلاعات بیشتر:
@mch_nsy
📢 کانال ما: 
@papoosh_charm

"""

class SimpleHealthCheckHandler(BaseHTTPRequestHandler):
def do_GET(self):
self.send_response(200)
self.end_headers()
self.wfile.write(b"Bot is active and running!")

def start_health_server():
port = int(os.environ.get("PORT", 8080))
server = HTTPServer(("0.0.0.0", port), SimpleHealthCheckHandler)
print(f"[*] Health server listening on port {port}", flush=True)
server.serve_forever()

def init_db():
conn = sqlite3.connect("posted_cache.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS posted (post_shortcode TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
conn.commit()
conn.close()

def is_already_posted(shortcode):
conn = sqlite3.connect("posted_cache.db")
cursor = conn.cursor()
cursor.execute("SELECT 1 FROM posted WHERE post_shortcode = ?", (shortcode,))
result = cursor.fetchone()
conn.close()
return result is not None

def mark_as_posted(shortcode):
conn = sqlite3.connect("posted_cache.db")
cursor = conn.cursor()
cursor.execute("INSERT OR IGNORE INTO posted (post_shortcode) VALUES (?)", (shortcode,))
conn.commit()
conn.close()

def clean_and_customize_caption(caption):
if not caption:
caption = ""
cleaned = re.sub(r"(+?98|0)?9\d{9}", "", caption)
cleaned = re.sub(r"@\w+", "", cleaned)
final_caption = f"{cleaned.strip()}\n\n{MY_FOOTER_SIGNATURE.strip()}"
return final_caption[:1020]

async def process_and_send():
if not TELEGRAM_BOT_TOKEN:
print("[!] Error: TELEGRAM_BOT_TOKEN not found in Environment Variables", flush=True)
return

bot = Bot(token=GAPGPTMASKTOKEN82h8pk33u4X0X
L = instaloader.Instaloader(
download_pictures=False,
download_videos=False,
download_video_thumbnails=False,
save_metadata=False,
compress_history=False
)

print(f"[*] Checking profile: {INSTAGRAM_TARGET_USERNAME}...", flush=True)
try:
profile = instaloader.Profile.from_username(L.context, INSTAGRAM_TARGET_USERNAME)
posts = profile.get_posts()

for post in list(posts)[:3]:
shortcode = post.shortcode
if is_already_posted(shortcode):
continue

print(f"[+] New post found: {shortcode}", flush=True)
caption = clean_and_customize_caption(post.caption)

if not post.is_sidecar:
if post.is_video:
await bot.send_video(chat_id=TELEGRAM_CHANNEL_ID, video=post.video_url, caption=caption)
else:
await bot.send_photo(chat_id=TELEGRAM_CHANNEL_ID, photo=post.url, caption=caption)
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
print(f"[OK] Posted: {shortcode}", flush=True)
await asyncio.sleep(5)

except Exception as e:
print(f"[!] Instagram error: {e}", flush=True)

async def main():
init_db()
health_thread = threading.Thread(target=start_health_server, daemon=True)
health_thread.start()

print("[*] Bot started successfully and running!", flush=True)
while True:
await process_and_send()
print(f"[*] Sleeping {CHECK_INTERVAL_SECONDS} seconds...", flush=True)
await asyncio.sleep(CHECK_INTERVAL_SECONDS)

asyncio.run(main())


