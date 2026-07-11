import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

# Tokenlar
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_TOKEN")

# Telegram ilovasi
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text(
        "Salom! Men Uznik AI man. Meni Kamronbek Xudaynazarov va Uznik Group yaratgan. "
        "Menga Roblox yoki boshqa xohlagan mavzuingizda savol berishingiz mumkin!"
    )

async def handle_message(update: Update, context):
    try:
        user_text = update.message.text
        client = genai.Client(api_key=GEMINI_KEY)
        
        instruction = (
            "Sening isming Uznik AI. Seni Kamronbek Xudaynazarov va Uznik Group jamoasi yaratgan. "
            "Sen har doim xushmuomala bo'lishing va foydalanuvchilarga yordam berishing kerak. "
            "Ayniqsa Roblox o'yini, skriptlar (Luau), mode-making va Roblox olamiga oid barcha narsalarni "
            "juda mukammal bilishing va bu mavzuda so'rashsa, batafsil va ekspertlardek javob berishing shart."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(system_instruction=instruction)
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Xatolik: {e}")
        await update.message.reply_text("Kechirasiz, tizim so'rovingizni qayta ishlay olmadi.")

# Handlerlarni sozlash
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Vercel uchun standart kirish klassi
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Kelgan ma'lumotni o'qish
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Telegram so'rovini asinxron qayta ishlash
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        update = Update.de_json(data, application.bot)
        
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.process_update(update))
        loop.close()
        
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        return

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Uznik AI active and ready.")
        return
