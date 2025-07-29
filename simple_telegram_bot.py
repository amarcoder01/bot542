#!/usr/bin/env python3
"""
Simplified Telegram Bot for TradeAI
Designed for reliable deployment with essential features
"""
import os
import asyncio
import logging
from typing import Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from aiohttp import web
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SimpleTelegramBot')

class SimpleTradingBot:
    """Simplified trading bot for deployment"""
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_API_TOKEN', '')
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.port = int(os.getenv('PORT', 8080))
        self.start_time = time.time()
        self.application = None
        self.web_app = None
        
        if not self.telegram_token:
            raise ValueError("TELEGRAM_API_TOKEN is required")
            
        logger.info("SimpleTradingBot initialized")
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """🤖 Welcome to TradeAI!

I'm your AI-powered trading companion. Here's what I can help you with:

📊 /price AAPL - Get stock prices
📈 /analyze TSLA - Market analysis  
📋 /help - Show all commands
💹 /market - Market overview

Type /help to see all available commands!"""
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        if not context.args:
            await update.message.reply_text("Please provide a stock symbol. Example: /price AAPL")
            return
            
        symbol = context.args[0].upper()
        
        # For now, return demo data - can be enhanced with real market data
        demo_response = f"""📊 {symbol} Stock Price

💰 Current: $150.25
📈 Change: +$2.15 (+1.45%)
📅 Last Update: Just now

⚠️ Demo mode - Connect market data APIs for real-time prices"""
        
        await update.message.reply_text(demo_response)
        logger.info(f"Price request for {symbol} from user {update.effective_user.id}")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        if not context.args:
            await update.message.reply_text("Please provide a stock symbol. Example: /analyze TSLA")
            return
            
        symbol = context.args[0].upper()
        
        # Demo analysis - can be enhanced with AI integration
        demo_analysis = f"""📈 {symbol} Analysis

🎯 Technical Indicators:
• Trend: Bullish
• RSI: 65 (Neutral)
• Support: $145.00
• Resistance: $155.00

💡 AI Insight: The stock shows strong momentum with good volume. Consider monitoring key resistance levels.

⚠️ Demo mode - Connect OpenAI for detailed AI analysis"""
        
        await update.message.reply_text(demo_analysis)
        logger.info(f"Analysis request for {symbol} from user {update.effective_user.id}")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        market_status = """📊 Market Overview

🇺🇸 US Markets:
• S&P 500: 4,450.25 (+0.5%)
• NASDAQ: 13,850.45 (+0.8%)
• DOW: 35,200.15 (+0.3%)

⏰ Market Status: Open
🕐 Last Update: Just now

💡 Tip: Use /analyze [SYMBOL] for detailed stock analysis!"""
        
        await update.message.reply_text(market_status)
        
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        
        status_text = f"""🤖 Bot Status

✅ Status: Online and Running
⏱️ Uptime: {hours}h {minutes}m
🔑 OpenAI: {'Connected' if self.openai_key else 'Not configured'}
📊 Version: 1.0.0

All systems operational!"""
        
        await update.message.reply_text(status_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_message = update.message.text.lower()
        
        if any(word in user_message for word in ['hello', 'hi', 'hey']):
            await update.message.reply_text("Hello! 👋 Type /help to see what I can do for you!")
        elif 'price' in user_message:
            await update.message.reply_text("To get stock prices, use: /price SYMBOL\nExample: /price AAPL")
        elif 'help' in user_message:
            await self.help_command(update, context)
        else:
            await update.message.reply_text("I didn't understand that. Type /help to see available commands!")
    
    async def error_handler(self, update: Optional[Update], context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    async def start_health_server(self):
        """Start health check web server"""
        async def health_check(request):
            uptime = int(time.time() - self.start_time)
            return web.json_response({
                'status': 'healthy',
                'uptime_seconds': uptime,
                'service': 'TradeAI Telegram Bot',
                'version': '1.0.0'
            })
        
        async def root_handler(request):
            return web.Response(text="TradeAI Telegram Bot is running!", status=200)
        
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        
        self.web_app = runner
        logger.info(f"Health server running on port {self.port}")
    
    async def run(self):
        """Main method to run the bot"""
        try:
            # Start health server
            await self.start_health_server()
            
            # Create Telegram application
            self.application = Application.builder().token(self.telegram_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            
            # Add message handler
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("🚀 TradeAI Telegram Bot starting...")
            logger.info(f"Bot features available:")
            logger.info("• Stock price queries (/price)")
            logger.info("• Market analysis (/analyze)")
            logger.info("• Market overview (/market)")
            logger.info("• Bot status (/status)")
            
            # Initialize and start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            # Keep running
            logger.info("✅ Bot is running and ready!")
            while True:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            if self.application:
                try:
                    await self.application.updater.stop()
                    await self.application.stop()
                    await self.application.shutdown()
                except:
                    pass
            if self.web_app:
                try:
                    await self.web_app.cleanup()
                except:
                    pass

async def main():
    """Main entry point"""
    try:
        bot = SimpleTradingBot()
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())