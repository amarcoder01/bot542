#!/usr/bin/env python3
"""
Working Telegram Bot for TradeAI - Fixed Import Issues
This version handles the telegram package import conflicts
"""
import os
import sys
import asyncio
import logging
import time
import json
from aiohttp import web
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('WorkingTelegramBot')

class WorkingTradingBot:
    """Working trading bot with proper telegram imports"""
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_API_TOKEN', '')
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.port = int(os.getenv('PORT', 8080))
        self.start_time = time.time()
        self.application = None
        self.web_app = None
        
        if not self.telegram_token:
            raise ValueError("TELEGRAM_API_TOKEN is required")
            
        logger.info("WorkingTradingBot initialized")
        
    def import_telegram_modules(self):
        """Safely import telegram modules with error handling"""
        try:
            # Remove any conflicting telegram module
            if 'telegram' in sys.modules:
                del sys.modules['telegram']
            
            # Try importing from the correct package path
            import importlib
            
            # First try the standard import
            try:
                from telegram import Update, Bot
                from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
                logger.info("Successfully imported telegram modules")
                return Update, Bot, Application, CommandHandler, MessageHandler, filters, ContextTypes
            except ImportError as e:
                logger.error(f"Failed to import telegram modules: {e}")
                
                # Try alternative import path
                try:
                    import python_telegram_bot
                    sys.modules['telegram'] = python_telegram_bot
                    from telegram import Update, Bot
                    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
                    logger.info("Successfully imported telegram modules via alternative path")
                    return Update, Bot, Application, CommandHandler, MessageHandler, filters, ContextTypes
                except ImportError as e2:
                    logger.error(f"Alternative import also failed: {e2}")
                    raise ImportError("Could not import telegram modules")
                    
        except Exception as e:
            logger.error(f"Critical error importing telegram modules: {e}")
            raise
    
    async def start_command(self, update, context):
        """Handle /start command"""
        welcome_message = """🤖 Welcome to TradeAI Working Bot!

I'm your AI-powered trading companion. Here's what I can help you with:

📊 /price AAPL - Get stock prices
📈 /analyze TSLA - Market analysis  
📋 /help - Show all commands
💹 /market - Market overview
🔧 /status - Bot status

Type /help to see all available commands!"""
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update, context):
        """Handle /help command"""
        help_text = """📋 TradeAI Commands:

🔍 Stock Commands:
/price [SYMBOL] - Get current stock price
/analyze [SYMBOL] - AI analysis of stock

📊 Market Commands:
/market - Market status overview
/news - Latest market news

🔧 Bot Commands:
/help - Show this help
/start - Welcome message
/status - Bot status

Example: /price AAPL or /analyze TSLA"""
        
        await update.message.reply_text(help_text)
        logger.info(f"Help command from user {update.effective_user.id}")
    
    async def status_command(self, update, context):
        """Handle /status command"""
        uptime = int(time.time() - self.start_time)
        status_text = f"""📊 Bot Status:

✅ Status: Online
⏱️ Uptime: {uptime} seconds
🔧 Version: Working v1.0
📡 Telegram API: Connected
🤖 AI Service: {'✅ Available' if self.openai_key else '❌ Not configured'}

The bot is running properly!"""
        
        await update.message.reply_text(status_text)
        logger.info(f"Status command from user {update.effective_user.id}")
    
    async def price_command(self, update, context):
        """Handle /price command"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /price AAPL")
                return
                
            symbol = context.args[0].upper()
            
            # Simple price response (real market data would require API integration)
            price_text = f"""📊 Stock Price for {symbol}:

💰 Current Price: Loading...
📈 Change: Loading...
📊 Volume: Loading...

Note: This is a working bot demonstration. 
Real market data integration requires additional API keys."""
            
            await update.message.reply_text(price_text)
            logger.info(f"Price command for {symbol} from user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text("Sorry, there was an error processing your request.")
    
    async def analyze_command(self, update, context):
        """Handle /analyze command"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /analyze TSLA")
                return
                
            symbol = context.args[0].upper()
            
            analysis_text = f"""🔍 AI Analysis for {symbol}:

📊 Technical Analysis: Loading...
📈 Trend: Loading...
🎯 Recommendation: Loading...
⚠️ Risk Level: Loading...

Note: This is a working bot demonstration.
Full AI analysis requires OpenAI API configuration."""
            
            await update.message.reply_text(analysis_text)
            logger.info(f"Analysis command for {symbol} from user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text("Sorry, there was an error processing your request.")
    
    async def market_command(self, update, context):
        """Handle /market command"""
        try:
            market_text = """📊 Market Overview:

🇺🇸 US Markets:
• S&P 500: Loading...
• NASDAQ: Loading...
• DOW: Loading...

🌍 Global Markets:
• FTSE: Loading...
• Nikkei: Loading...
• DAX: Loading...

📈 Market Sentiment: Loading...

Note: This is a working bot demonstration.
Real market data requires API integration."""
            
            await update.message.reply_text(market_text)
            logger.info(f"Market command from user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in market command: {e}")
            await update.message.reply_text("Sorry, there was an error processing your request.")
    
    async def handle_message(self, update, context):
        """Handle regular messages"""
        try:
            user_message = update.message.text.lower()
            
            if any(word in user_message for word in ['hello', 'hi', 'hey']):
                response = """👋 Hello! I'm TradeAI, your trading assistant.

Type /help to see what I can do, or try:
• /price AAPL - for stock prices
• /market - for market overview
• /analyze TSLA - for stock analysis"""
                
            elif any(word in user_message for word in ['thanks', 'thank you']):
                response = "You're welcome! Happy to help with your trading needs! 📊"
                
            else:
                response = """I'm not sure I understand that command. 

Try:
• /help - See all commands
• /price [SYMBOL] - Get stock prices
• /market - Market overview

Or just ask me about stocks and markets!"""
            
            await update.message.reply_text(response)
            logger.info(f"Message handled from user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Sorry, I couldn't process that message.")
    
    async def setup_telegram_bot(self):
        """Setup the Telegram bot with proper imports"""
        try:
            # Import telegram modules safely
            Update, Bot, Application, CommandHandler, MessageHandler, filters, ContextTypes = self.import_telegram_modules()
            
            # Create application
            self.application = Application.builder().token(self.telegram_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            logger.info("Telegram bot setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup Telegram bot: {e}")
            return False
    
    async def setup_health_server(self):
        """Setup health check web server"""
        try:
            async def health_check(request):
                return web.json_response({
                    'status': 'healthy',
                    'bot': 'working_telegram_bot',
                    'uptime': int(time.time() - self.start_time),
                    'telegram_configured': bool(self.telegram_token),
                    'openai_configured': bool(self.openai_key)
                })
            
            async def stats(request):
                return web.json_response({
                    'uptime': int(time.time() - self.start_time),
                    'status': 'running',
                    'version': 'working_v1.0'
                })
            
            self.web_app = web.Application()
            self.web_app.router.add_get('/health', health_check)
            self.web_app.router.add_get('/stats', stats)
            self.web_app.router.add_get('/', health_check)
            
            logger.info(f"Health server configured on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup health server: {e}")
            return False
    
    async def run(self):
        """Run the bot"""
        try:
            logger.info("=== Starting Working Telegram Bot ===")
            
            # Setup Telegram bot
            if not await self.setup_telegram_bot():
                logger.error("Failed to setup Telegram bot")
                return
            
            # Setup health server
            if not await self.setup_health_server():
                logger.error("Failed to setup health server")
                return
            
            # Start health server
            runner = web.AppRunner(self.web_app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            logger.info(f"✅ Health server started on port {self.port}")
            
            # Start Telegram bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("✅ Telegram bot started successfully")
            
            logger.info("🚀 Working Telegram Bot is fully operational!")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
            
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            raise
        finally:
            # Cleanup
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot stopped")
            
            if runner:
                await runner.cleanup()
                logger.info("Health server stopped")

async def main():
    """Main entry point"""
    try:
        bot = WorkingTradingBot()
        await bot.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())