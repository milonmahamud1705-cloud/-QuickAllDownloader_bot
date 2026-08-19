import os
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8786560452:AAHQG7_d-MXlEFsEntmc4mov_nVQRsfyOPE"

# Render-কে লাইভ রাখার জন্য ব্যাকগ্রাউন্ড ওয়েব সার্ভার
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
        "👋 স্বাগতম! আমি একটি অল-ইন-ওয়ান ভিডিও ডাউনলোডার বট।\n\n"
        "যেকোনো ওয়েবসাইটের ভিডিও লিংক পাঠান, আমি সেটি ডাউনলোড করে দেব।"
    )
    await update.message.reply_text(welcome_text)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("❌ অনুগ্রহ করে একটি সঠিক ওয়েব লিংক পাঠান।")
        return

    status_msg = await update.message.reply_text("⏳ ভিডিও প্রসেস হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        caption = "✅ Downloaded successfully!\n\n🤖 Powered by @QuickAllDownloader_bot"
        
        await status_msg.edit_text("📤 ভিডিও টেলিগ্রামে আপলোড হচ্ছে...")

        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption=caption)

        if os.path.exists(file_path):
            os.remove(file_path)
            
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ ভিডিও ডাউনলোড করা সম্ভব হয়নি। ফাইলের সাইজ ৫০ MB-এর বেশি হতে পারে অথবা লিংকটি কাজ করছে না।")

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    # ব্যাকগ্রাউন্ড ওয়েব সার্ভার চালু
    Thread(target=run_web_server, daemon=True).start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    app.run_polling()
