#!/usr/bin/env python3
"""Test telegram imports"""
try:
    from telegram import Update, Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    print("✅ Telegram imports successful")
    print(f"Telegram version: {telegram.__version__}")
except Exception as e:
    print(f"❌ Import error: {e}")
    
try:
    import telegram
    print(f"Telegram module location: {telegram.__file__}")
    print(f"Available items: {dir(telegram)}")
except Exception as e:
    print(f"❌ Module error: {e}")