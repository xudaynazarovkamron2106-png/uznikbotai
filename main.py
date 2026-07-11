import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from google.genai import types

# Vercel va atrof-muhit o'zgaruvchilari (Karta so'ramasligi va xavfsizlik uchun)
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8911290591:AAFYH6WS5JjQkfGSVUpHBje2iMHFxzpBo0A")
GEMINI_KEY = os.environ.get("GEMINI_TOKEN", "AQ.Ab8RN6JSUZaF05aLk0mQ2y72isaqbtha_TmAO6ZrO9WRYViLRQ")

class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Uznik AI is running perfectly!")

def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men Uznik AI man. Meni Kamronbek Xudaynazarov va Uznik Group yaratgan. "
        "Menga Roblox yoki boshqa xohlagan mavzuingizda savol berishingiz mumkin!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
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
        await update.message.reply_text("Kechirasiz, tizim so'rovingizni qayta ishlay olmadi.")

# Vercel uchun kirish funksiyasi
def handler(request, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b"Bot status: Active"]

def main():
    threading.Thread(target=run_health_server, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()
