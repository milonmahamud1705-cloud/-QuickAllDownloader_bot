import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# আপনার বটের টোকেন এখানে যুক্ত করা আছে
BOT_TOKEN = "8786560452:AAHQG7_d-MXlEFsEntmc4mov_nVQRsfyOPE"

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

    status_msg = await update.message.reply_text("⏳ ভিডিও এক্সট্র্যাক্ট করা হচ্ছে, অপেক্ষা করুন...")

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
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    app.run_polling()
