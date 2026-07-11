import os
import json
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from google import genai
from google.genai import types

# Tokenlarni Vercel'dan olamiz
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_TOKEN")

# Telegram Application-ni sozlash
# Vercel-da pooling ishlamagani uchun faqat webhook yoki oddiy boshqaruv ishlatamiz
application = Application.builder().token(TOKEN).build()

# FastAPI ilovasini yaratamiz (Vercel buni avtomatik taniydi)
app = FastAPI()

async def start(update: Update, context):
    await update.message.reply_text(
        "Salom! Men Uznik AI man. Meni Kamronbek Xudaynazarov va Uznik Group yaratgan. "
        "Menga Roblox yoki boshqa xohlagan mavzuingizda savol berishingiz mumkin!"
    )

async def handle_message(update: Update, context):
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

# Handlerlarni ro'yxatdan o'tkazish
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.on_event("startup")
async def startup_event():
    await application.initialize()

@app.post("/api/webhook")
async def webhook(request: Request):
    """Telegramdan kelgan xabarlarni qabul qilish"""
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"Uznik AI": "Active"}
