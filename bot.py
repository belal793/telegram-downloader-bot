import yt_dlp
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8739713856:AAFJY3WKf2hZCvS4h2HqSStWLTvYmRlUjlY"

user_links = {}

# استقبال اللينك
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not url.startswith("http"):
        await update.message.reply_text("❗ ابعت لينك فيديو صحيح")
        return

    user_links[update.message.chat_id] = url

    keyboard = [
        [InlineKeyboardButton("🎥 فيديو", callback_data="video")],
        [InlineKeyboardButton("🎧 صوت MP3", callback_data="audio")]
    ]

    await update.message.reply_text("اختار النوع 👇", reply_markup=InlineKeyboardMarkup(keyboard))


# التعامل مع الأزرار
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    url = user_links.get(chat_id)

    if not url:
        await query.message.reply_text("❌ حصل خطأ")
        return

    # اختيار فيديو
    if query.data == "video":
        keyboard = [
            [InlineKeyboardButton("360p", callback_data="360")],
            [InlineKeyboardButton("720p", callback_data="720")],
            [InlineKeyboardButton("أفضل جودة", callback_data="best")]
        ]
        await query.message.reply_text("اختار الجودة 👇", reply_markup=InlineKeyboardMarkup(keyboard))

    # اختيار صوت
    elif query.data == "audio":
        await query.message.reply_text("⏳ جاري تحميل الصوت...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                filename = ydl.prepare_filename(info)
                filename = os.path.splitext(filename)[0] + ".mp3"

            if os.path.exists(filename):
                with open(filename, "rb") as audio:
                    await query.message.reply_audio(audio)

                os.remove(filename)
            else:
                await query.message.reply_text("❌ الملف مش موجود")

        except Exception as e:
            print(e)
            await query.message.reply_text("❌ فشل تحميل الصوت")

    # اختيار الجودة
    elif query.data in ["360", "720", "best"]:
        await query.message.reply_text("⏳ جاري تحميل الفيديو...")

        if query.data == "360":
            fmt = "best[height<=360]/best"
        elif query.data == "720":
            fmt = "best[height<=720]/best"
        else:
            fmt = "best"

        ydl_opts = {
            'format': fmt,
            'outtmpl': '%(title)s.%(ext)s',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            with open(filename, "rb") as video:
                await query.message.reply_video(video)

            os.remove(filename)

        except Exception as e:
            print(e)
            await query.message.reply_text("❌ فشل تحميل الفيديو")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handle_message))
app.add_handler(CallbackQueryHandler(handle_buttons))

app.run_polling()
