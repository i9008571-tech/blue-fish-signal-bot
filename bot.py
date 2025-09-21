#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import random
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN', '8360851879:AAFVWn67KnWgpTuZkbqF3HX3zNlqfqsGUZc')
PORT = int(os.environ.get('PORT', 5000))

# User Session Storage
user_sessions = {}

# Assets List
OTC_ASSETS = [
    "BRLUSD-OTC", "USDNGN-OTC", "USDCOP-OTC", "USDTRY-OTC", "USDZAR-OTC", 
    "BTCUSD-OTC", "USDARS-OTC", "INTC-OTC", "USDPKR-OTC", "USDBDT-OTC", 
    "MCD-OTC", "JNJ-OTC", "BA-OTC", "CADCHF-OTC", "USDJPY-OTC", 
    "USDCAD-OTC", "USDPHP-OTC", "USDMXN-OTC", "USDINR-OTC", "USDEGP-OTC", 
    "USDDZD-OTC", "PFE-OTC", "MSFT-OTC", "USCRUDE-OTC", "UKBRENT-OTC", 
    "FB-OTC", "GBPJPY-OTC", "GBPUSD-OTC", "AUDCAD-OTC", "AUDCHF-OTC", 
    "AUDJPY-OTC", "AUDNZD-OTC", "AUDUSD-OTC", "CADJPY-OTC", "CHFJPY-OTC", 
    "EURJPY-OTC"
]

class UserSession:
    def __init__(self):
        self.step = "start"
        self.license_valid = False
        self.username = ""
        self.market_type = ""
        self.selected_assets = []
        self.signal_type = ""
        self.confidence = 0
        self.analysis_day = 0
        self.start_time = ""
        self.end_time = ""

def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession()
    return user_sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_user_session(user_id)
    session.step = "license"
    
    welcome_text = """══════════════════════════════════════════════════
       🚀 BLUE FISH X SIGNAL GENERATOR V9.5 🚀
       Developed by: LITTLE MATRIX
       Telegram: @LittleMatrix
       Version: 9.5 | Time Zone: UTC+6
══════════════════════════════════════════════════

🔑 Please enter your license key (e.g., BLUEFISH2025):"""
    
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    session = get_user_session(user_id)
    
    try:
        if session.step == "license":
            await handle_license(update, session, message_text)
        elif session.step == "username":
            await handle_username(update, session, message_text)
        elif session.step == "password":
            await handle_password(update, session, message_text)
        elif session.step == "market":
            await handle_market(update, session, message_text)
        elif session.step == "assets":
            await handle_assets(update, session, message_text)
        elif session.step == "signal_type":
            await handle_signal_type(update, session, message_text)
        elif session.step == "confidence":
            await handle_confidence(update, session, message_text)
        elif session.step == "analysis_day":
            await handle_analysis_day(update, session, message_text)
        elif session.step == "start_time":
            await handle_start_time(update, session, message_text)
        elif session.step == "end_time":
            await handle_end_time(update, session, message_text)
        elif session.step == "confirmation":
            await handle_confirmation(update, session, message_text)
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again.")

async def handle_license(update, session, message_text):
    session.license_valid = True
    session.step = "username"
    await update.message.reply_text("✅ License is valid!\n\n🔑 Enter your username:")

async def handle_username(update, session, message_text):
    session.username = message_text
    session.step = "password"
    await update.message.reply_text("🔑 Enter your password:")

async def handle_password(update, session, message_text):
    session.step = "market"
    await update.message.reply_text(f"✅ Welcome, {session.username}!\n\n📊 Choose Market Type:\n1. OTC Market\n2. Real Market\n\nEnter 1 or 2:")

async def handle_market(update, session, message_text):
    if message_text == "1":
        session.market_type = "OTC"
        session.step = "assets"
        
        assets_text = "✅ OTC Market selected!\n\n📊 Available Assets:\n"
        for i, asset in enumerate(OTC_ASSETS, 1):
            if i % 3 == 1:
                assets_text += f"{i}. {asset:<15}"
            elif i % 3 == 2:
                assets_text += f"{i}. {asset:<15}"
            else:
                assets_text += f"{i}. {asset}\n"
        
        assets_text += "\n\nEnter asset numbers (e.g., 1,3,5 or 'all' for all assets):"
        await update.message.reply_text(assets_text)
    elif message_text == "2":
        await update.message.reply_text("❌ Real Market is not available in demo version.")
    else:
        await update.message.reply_text("❌ Please enter 1 or 2.")

async def handle_assets(update, session, message_text):
    if message_text.lower() == "all":
        session.selected_assets = OTC_ASSETS.copy()
        session.step = "signal_type"
        await update.message.reply_text("✅ Selected all assets!\n\n📈 Choose Signal Type:\n1. CALL Only\n2. PUT Only\n3. Both (CALL & PUT)\n\nEnter 1, 2, or 3:")
    else:
        try:
            numbers = [int(x.strip()) for x in message_text.split(",")]
            selected = []
            for num in numbers:
                if 1 <= num <= len(OTC_ASSETS):
                    selected.append(OTC_ASSETS[num-1])
            
            if selected:
                session.selected_assets = selected
                session.step = "signal_type"
                await update.message.reply_text("✅ Assets selected!\n\n📈 Choose Signal Type:\n1. CALL Only\n2. PUT Only\n3. Both (CALL & PUT)\n\nEnter 1, 2, or 3:")
            else:
                await update.message.reply_text("❌ Invalid asset numbers. Please try again.")
        except ValueError:
            await update.message.reply_text("❌ Invalid format. Use numbers separated by commas or 'all'.")

async def handle_signal_type(update, session, message_text):
    if message_text == "1":
        session.signal_type = "CALL"
        session.step = "confidence"
        await update.message.reply_text("✅ Signal type set to CALL!\n\n📉 Set Minimum Confidence (80-100%):\nEnter a number (e.g., 85):")
    elif message_text == "2":
        session.signal_type = "PUT"
        session.step = "confidence"
        await update.message.reply_text("✅ Signal type set to PUT!\n\n📉 Set Minimum Confidence (80-100%):\nEnter a number (e.g., 85):")
    elif message_text == "3":
        session.signal_type = "BOTH"
        session.step = "confidence"
        await update.message.reply_text("✅ Signal type set to BOTH!\n\n📉 Set Minimum Confidence (80-100%):\nEnter a number (e.g., 85):")
    else:
        await update.message.reply_text("❌ Please enter 1, 2, or 3.")

async def handle_confidence(update, session, message_text):
    try:
        confidence = int(message_text)
        if 80 <= confidence <= 100:
            session.confidence = confidence
            session.step = "analysis_day"
            await update.message.reply_text("✅ Confidence level set!\n\n📅 Choose Analysis Day (1-10 days ago):\nEnter a number (e.g., 1 for yesterday):")
        else:
            await update.message.reply_text("❌ Please enter a number between 80 and 100.")
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")

async def handle_analysis_day(update, session, message_text):
    try:
        day = int(message_text)
        if 1 <= day <= 10:
            session.analysis_day = day
            session.step = "start_time"
            await update.message.reply_text("✅ Analysis day set!\n\n⏰ Set Start Time (HH:MM, UTC+6):\nEnter time (e.g., 09:00):")
        else:
            await update.message.reply_text("❌ Please enter a number between 1 and 10.")
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number.")

async def handle_start_time(update, session, message_text):
    if validate_time_format(message_text):
        session.start_time = message_text
        session.step = "end_time"
        await update.message.reply_text("⏰ Set End Time (HH:MM, UTC+6):\nEnter time (e.g., 17:00):")
    else:
        await update.message.reply_text("❌ Invalid time format. Please use HH:MM format (e.g., 09:00).")

async def handle_end_time(update, session, message_text):
    if validate_time_format(message_text):
        session.end_time = message_text
        session.step = "confirmation"
        
        assets_str = ", ".join(session.selected_assets)
        confirmation_text = f"""📋 Your Selections:
Market: {session.market_type}
Assets: {assets_str}
Signal Type: {session.signal_type}
Confidence: {session.confidence}%
Analysis Day: {session.analysis_day} days ago
Time Range: {session.start_time} to {session.end_time}

Is this correct? Reply 'yes' to generate signals or 'no' to start over."""
        
        await update.message.reply_text(confirmation_text)
    else:
        await update.message.reply_text("❌ Invalid time format. Please use HH:MM format (e.g., 17:00).")

async def handle_confirmation(update, session, message_text):
    if message_text.lower() == "yes":
        await generate_signals(update, session)
        session.step = "start"  # Reset session
    elif message_text.lower() == "no":
        session.step = "license"
        await update.message.reply_text("🔄 Starting over...\n\n🔑 Please enter your license key:")
    else:
        await update.message.reply_text("❌ Please reply 'yes' or 'no'.")

def validate_time_format(time_str):
    try:
        datetime.datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

async def generate_signals(update, session):
    await update.message.reply_text("📡 Generating signals...")
    
    # Generate random signals
    signals = []
    signal_count = random.randint(15, 30)
    
    start_hour, start_minute = map(int, session.start_time.split(":"))
    end_hour, end_minute = map(int, session.end_time.split(":"))
    
    for _ in range(signal_count):
        asset = random.choice(session.selected_assets)
        
        # Generate random time within range
        hour = random.randint(start_hour, end_hour)
        if hour == end_hour:
            minute = random.randint(0, end_minute)
        else:
            minute = random.randint(0, 59)
        
        time_str = f"{hour:02d}:{minute:02d}"
        
        # Generate signal type
        if session.signal_type == "BOTH":
            signal_type = random.choice(["CALL", "PUT"])
        else:
            signal_type = session.signal_type
        
        signals.append(f"M1 {asset} {time_str} {signal_type}")
    
    # Sort signals by time
    signals.sort(key=lambda x: x.split()[2])
    
    # Create signal message
    today = datetime.datetime.now()
    signal_date = today - datetime.timedelta(days=session.analysis_day)
    date_str = signal_date.strftime("%d/%m/%Y")
    
    signal_text = f"""𒆜•--❎ 𝗙𝗜𝗡𝗔𝗟 ⋅◈⋅ SIGNAL ❎--•𒆜
━━━━━━━━━・━━━━━━━━━
📆 {date_str} 📆
━━━━━━━━━・━━━━━━━━━
SIGNAL FOR QUOTEX

UTC+6 TIME ZONE

1 MIN SIGNAL, USE 1 STEP MTG MAX

MIN CONFIDENCE: {session.confidence}%

"""
    
    for signal in signals:
        signal_text += signal + "\n"
    
    signal_text += """━━━━━━━━━・━━━━━━━━━
❗️ AVOID SIGNAL AFTER BIG CANDLE,
❗️ DOJI, BELOW 80% & GAP
━━━━━━━━━・━━━━━━━━━
❤️•-------‼️ B╎K╎P ‼️-------•❤️

✅ Signals saved to file!"""
    
    await update.message.reply_text(signal_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    """Run the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Run the bot
    logger.info("Starting Blue Fish Signal Bot...")
    
    # For local development
    if os.environ.get('ENVIRONMENT') == 'local':
        application.run_polling()
    else:
        # For production (Heroku/Railway)
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"https://your-app-name.herokuapp.com/{BOT_TOKEN}"
        )

if __name__ == '__main__':
    main()
