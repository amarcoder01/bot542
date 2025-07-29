#!/usr/bin/env python3
"""
Minimal test to isolate the timezone issue
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set timezone environment variables
os.environ['TZ'] = 'UTC'
os.environ['APSCHEDULER_TIMEZONE'] = 'UTC'
if hasattr(os, 'tzset'):
    os.tzset()

# Import pytz
import pytz

print("Testing telegram bot initialization...")

try:
    from telegram.ext import Application
    
    # Get bot token
    bot_token = os.getenv('TELEGRAM_API_TOKEN')
    if not bot_token:
        print("Error: TELEGRAM_API_TOKEN not found in environment")
        exit(1)
    
    print(f"Bot token found: {bot_token[:10]}...")
    
    # Try different initialization approaches
    print("\n1. Testing basic Application.builder()...")
    try:
        app1 = Application.builder().token(bot_token).build()
        print("✅ Basic Application.builder() works")
    except Exception as e:
        print(f"❌ Basic Application.builder() failed: {e}")
    
    print("\n2. Testing Application.builder() with job_queue=None...")
    try:
        app2 = Application.builder().token(bot_token).job_queue(None).build()
        print("✅ Application.builder() with job_queue=None works")
    except Exception as e:
        print(f"❌ Application.builder() with job_queue=None failed: {e}")
    
    print("\n3. Testing Application initialization...")
    try:
        app3 = Application.builder().token(bot_token).job_queue(None).build()
        asyncio.run(app3.initialize())
        print("✅ Application initialization works")
        asyncio.run(app3.shutdown())
    except Exception as e:
        print(f"❌ Application initialization failed: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    print(f"Full traceback: {traceback.format_exc()}")

print("\nTest completed.")