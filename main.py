import os
import glob
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8786560452:AAHQG7_d-MXlEFsEntmc4mov_nVQRsfyOPE"

# Background web server to keep Render alive 24/7
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome! I am an All-in-One Video Downloader Bot.\n\n"
        "Send me any video link (Instagram, TikTok, Facebook, YouTube, etc.) and I will download it for you!"
    )
    await update.message.reply_text(welcome_text)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ Please provide a valid URL link.")
        return

    status_msg = await update.message.reply_text("⏳ Processing your video, please wait...")

    # yt-dlp configuration with mobile headers
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id', 'video')

        # Find downloaded file
        files = glob.glob(f"downloads/{video_id}.*")
        if not files:
            files = glob.glob("downloads/*")

        if files:
            file_path = files[0]
            await status_msg.edit_text("📤 Uploading video to Telegram...")
            
            with open(file_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file, 
                    caption="✅ Downloaded successfully!\n\n🤖 Powered by @QuickAllDownloader_bot",
                    read_timeout=120,
                    write_timeout=120
                )
            
            if os.path.exists(file_path):
                os.remove(file_path)
            await status_msg.delete()
        else:
            await status_msg.edit_text("❌ Failed to find the downloaded file.")

    except Exception as e:
        err = str(e)
        if "File is larger than max_filesize" in err:
            await status_msg.edit_text("❌ The video is larger than 50 MB (Telegram bot limit).")
        else:
            await status_msg.edit_text("❌ Unable to download video. Please ensure the link is valid and public.")

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    Thread(target=run_web_server, daemon=True).start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    app.run_polling()
