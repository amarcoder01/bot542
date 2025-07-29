#!/usr/bin/env python3
"""
TradeAI Integrated Bot - Simplified version that works without complex dependencies
Integrates features from deploy folder while handling missing dependencies gracefully
"""
import os
import sys
import asyncio
import logging
import time
import json
from typing import Optional, Dict, List
from pathlib import Path
from aiohttp import web
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TradeAI')

# Import Telegram components
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Simple implementations for essential services when full services aren't available
class SimpleMarketService:
    """Simplified market data service"""
    async def get_stock_price(self, symbol: str, user_id: int = None) -> Dict:
        """Get simulated stock price data"""
        # In production, this would fetch real data
        return {
            'symbol': symbol,
            'price': 150.00,
            'change': 2.50,
            'change_percent': 1.67,
            'volume': 1000000,
            'day_low': 147.50,
            'day_high': 152.00,
            'low_52w': 120.00,
            'high_52w': 180.00,
            'market_cap': '2.5T',
            'pe_ratio': 25.5,
            'company_name': f'{symbol} Inc.',
            'error': 'Real-time data requires API configuration'
        }
    
    async def get_market_summary(self) -> Dict:
        """Get simulated market summary"""
        return {
            'indices': {
                'S&P 500': '5,000.00 (+0.5%)',
                'NASDAQ': '15,000.00 (+0.8%)',
                'DOW': '40,000.00 (+0.3%)',
                'FTSE': '7,500.00 (+0.2%)',
                'NIKKEI': '35,000.00 (-0.1%)',
                'DAX': '18,000.00 (+0.4%)'
            },
            'sentiment': 'Bullish',
            'error': 'Real-time data requires API configuration'
        }

class SimpleAIService:
    """Simplified AI service"""
    async def generate_response(self, user_message: str, user_id: int) -> str:
        """Generate simple response without OpenAI"""
        return (
            "I'm currently running in simplified mode. "
            "To enable AI-powered responses, please configure the OpenAI API key. "
            f"You asked: {user_message}"
        )

class SimpleAlertService:
    """Simplified alert service"""
    def __init__(self):
        self.alerts = {}
        self.next_id = 1
    
    async def add_alert(self, telegram_user_id: int, symbol: str, condition: str, target_price: float) -> Dict:
        """Add alert to memory"""
        alert_id = self.next_id
        self.next_id += 1
        
        if telegram_user_id not in self.alerts:
            self.alerts[telegram_user_id] = []
        
        self.alerts[telegram_user_id].append({
            'id': alert_id,
            'symbol': symbol,
            'condition': f"{condition} {target_price:.2f}",
            'target_price': target_price,
            'active': True
        })
        
        return {'success': True, 'alert_id': alert_id, 'message': 'Alert created (in-memory only)'}
    
    async def get_user_alerts(self, telegram_user_id: int) -> List[Dict]:
        """Get user alerts"""
        return self.alerts.get(telegram_user_id, [])
    
    async def start_monitoring(self):
        """Placeholder for alert monitoring"""
        logger.info("Alert monitoring started (simplified mode)")

class TradeAIIntegratedBot:
    """Integrated Trading Bot with graceful fallback"""
    
    def __init__(self):
        """Initialize bot with available services"""
        self.telegram_token = os.getenv('TELEGRAM_API_TOKEN', '')
        self.port = int(os.getenv('PORT', 5000))
        self.start_time = time.time()
        
        if not self.telegram_token:
            raise ValueError("TELEGRAM_API_TOKEN is required")
        
        logger.info("🚀 Initializing TradeAI Integrated Bot...")
        
        # Try to import from deploy folder, fallback to simple implementations
        deploy_dir = Path(__file__).parent / 'deploy'
        if deploy_dir.exists():
            sys.path.insert(0, str(deploy_dir))
        
        # Initialize services with fallback
        self._init_services()
        
        # Telegram application
        self.application = None
        self.web_app = None
        
        logger.info("✅ Bot initialized with available services")
    
    def _init_services(self):
        """Initialize services with graceful fallback"""
        # Market service
        try:
            from market_data_service import MarketDataService
            self.market_service = MarketDataService()
            logger.info("✅ Full MarketDataService loaded")
        except:
            self.market_service = SimpleMarketService()
            logger.warning("⚠️ Using simplified market service")
        
        # AI service
        try:
            from openai_service import OpenAIService
            self.ai_service = OpenAIService()
            logger.info("✅ Full OpenAIService loaded")
        except:
            self.ai_service = SimpleAIService()
            logger.warning("⚠️ Using simplified AI service")
        
        # Alert service
        try:
            from alert_service import AlertService
            self.alert_service = AlertService(self.market_service, self.send_alert_notification)
            logger.info("✅ Full AlertService loaded")
        except:
            self.alert_service = SimpleAlertService()
            logger.warning("⚠️ Using simplified alert service")
        
        # Optional services
        self.chart_service = None
        self.trading_intelligence = None
        self.portfolio_optimizer = None
        self.qlib_service = None
        
        try:
            from chart_service import ChartService
            self.chart_service = ChartService()
            logger.info("✅ ChartService loaded")
        except:
            logger.info("ℹ️ ChartService not available")
        
        try:
            from trading_intelligence import TradingIntelligence
            self.trading_intelligence = TradingIntelligence()
            logger.info("✅ TradingIntelligence loaded")
        except:
            logger.info("ℹ️ TradingIntelligence not available")
        
        try:
            from portfolio_optimizer import ModernPortfolioOptimizer
            self.portfolio_optimizer = ModernPortfolioOptimizer()
            logger.info("✅ PortfolioOptimizer loaded")
        except:
            logger.info("ℹ️ PortfolioOptimizer not available")
        
        try:
            from qlib_service import QlibService
            self.qlib_service = QlibService()
            logger.info("✅ QlibService loaded")
        except:
            logger.info("ℹ️ QlibService not available")
    
    async def send_alert_notification(self, user_id: int, message: str):
        """Send alert notification to user"""
        try:
            if self.application and self.application.bot:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"🚨 Alert Triggered!\n\n{message}"
                )
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    # Command Handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """🤖 Welcome to TradeAI Integrated Bot!

I'm your comprehensive trading assistant with multiple features:

📊 **Core Features:**
• /price AAPL - Get stock prices
• /market - Market overview
• /alert AAPL above 150 - Set price alerts
• /alerts - View your alerts
• /chat - Chat with AI assistant
• /help - See all commands
• /status - Bot status

🚀 **Advanced Features (when available):**
• /analyze - AI-powered analysis
• /signal - Trading signals
• /portfolio - Portfolio optimization
• /chart - Price charts

Type /help for detailed commands or just chat naturally!"""
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """📋 **TradeAI Commands**

**📊 Always Available:**
/price [SYMBOL] - Stock price
/market - Market overview
/alert [SYMBOL] [above/below] [PRICE] - Set alert
/alerts - View alerts
/chat [message] - AI chat
/status - Bot status
/help - This menu

**🔧 Advanced (if configured):**
/analyze [SYMBOL] - Deep analysis
/signal [SYMBOL] - Trading signals
/portfolio AAPL,MSFT,GOOGL - Optimize
/chart [SYMBOL] - Price charts

💡 **Examples:**
• /price TSLA
• /alert AAPL above 150
• /chat What's the market outlook?

Note: Some features require API configuration."""
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        # Check which services are available
        services_status = {
            'Market Data': '✅' if hasattr(self.market_service, 'get_stock_price') else '❌',
            'AI Service': '✅' if self.ai_service else '❌',
            'Alerts': '✅' if self.alert_service else '❌',
            'Charts': '✅' if self.chart_service else '⚠️ Not configured',
            'Trading AI': '✅' if self.trading_intelligence else '⚠️ Not configured',
            'Portfolio': '✅' if self.portfolio_optimizer else '⚠️ Not configured',
            'Qlib': '✅' if self.qlib_service else '⚠️ Not configured'
        }
        
        status_text = f"""📊 **TradeAI Bot Status**

✅ Status: Operational
⏱️ Uptime: {hours}h {minutes}m {seconds}s
🔧 Version: Integrated 2.0

📡 **Services:**
"""
        for service, status in services_status.items():
            status_text += f"• {service}: {status}\n"
        
        status_text += """
💡 Core features are operational.
Some advanced features may require additional configuration."""
        
        await update.message.reply_text(status_text)
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /price AAPL")
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🔍 Fetching price data for {symbol}...")
            
            # Get price data
            price_data = await self.market_service.get_stock_price(symbol, update.effective_user.id)
            
            # Format response
            if 'error' in price_data:
                response = f"📊 **{symbol}**\n\n"
                response += f"💵 Price: ${price_data.get('price', 'N/A')}\n"
                response += f"📈 Change: {price_data.get('change_percent', 'N/A')}%\n\n"
                response += f"⚠️ Note: {price_data['error']}"
            else:
                response = f"""📊 **{price_data.get('company_name', symbol)}** ({symbol})

💵 Price: ${price_data.get('price', 'N/A'):.2f}
📈 Change: {price_data.get('change', 'N/A'):.2f} ({price_data.get('change_percent', 'N/A'):.2f}%)
📊 Volume: {price_data.get('volume', 'N/A'):,}

📈 Day Range: ${price_data.get('day_low', 'N/A'):.2f} - ${price_data.get('day_high', 'N/A'):.2f}
💹 Market Cap: {price_data.get('market_cap', 'N/A')}

🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            await update.message.reply_text(response)
            
            # Try to send chart if available
            if self.chart_service:
                try:
                    chart_url = await self.chart_service.generate_price_chart(symbol, period='1mo')
                    if chart_url:
                        await update.message.reply_photo(
                            photo=chart_url,
                            caption=f"📈 1 Month Chart for {symbol}"
                        )
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching the price data.")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        try:
            await update.message.reply_text("📊 Fetching market overview...")
            
            market_data = await self.market_service.get_market_summary()
            
            indices = market_data.get('indices', {})
            response = "📊 **Market Overview**\n\n**Major Indices:**\n"
            
            for index, value in indices.items():
                response += f"• {index}: {value}\n"
            
            if 'error' in market_data:
                response += f"\n⚠️ Note: {market_data['error']}"
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error in market command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching market data.")
    
    async def alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alert command"""
        try:
            if len(context.args) < 3:
                await update.message.reply_text(
                    "Usage: /alert [SYMBOL] [above/below] [PRICE]\n"
                    "Example: /alert AAPL above 150"
                )
                return
            
            symbol = context.args[0].upper()
            condition = context.args[1].lower()
            
            try:
                target_price = float(context.args[2])
            except ValueError:
                await update.message.reply_text("Please provide a valid price number.")
                return
            
            if condition not in ['above', 'below']:
                await update.message.reply_text("Condition must be 'above' or 'below'.")
                return
            
            # Add alert
            result = await self.alert_service.add_alert(
                telegram_user_id=update.effective_user.id,
                symbol=symbol,
                condition=condition,
                target_price=target_price
            )
            
            if result['success']:
                await update.message.reply_text(
                    f"✅ Alert set successfully!\n\n"
                    f"📊 {symbol} {condition} ${target_price:.2f}\n"
                    f"🔔 Alert ID: {result['alert_id']}\n\n"
                    f"You'll be notified when the condition is met."
                )
            else:
                await update.message.reply_text(f"❌ Failed to set alert: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            logger.error(f"Error in alert command: {e}")
            await update.message.reply_text("Sorry, there was an error setting the alert.")
    
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        try:
            alerts = await self.alert_service.get_user_alerts(update.effective_user.id)
            
            if not alerts:
                await update.message.reply_text("You don't have any active alerts. Use /alert to create one.")
                return
            
            response = "🚨 **Your Active Alerts:**\n\n"
            for alert in alerts:
                response += f"• Alert #{alert['id']}: {alert['symbol']} {alert['condition']}\n"
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error in alerts command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching your alerts.")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        if not self.trading_intelligence:
            await update.message.reply_text(
                "⚠️ Advanced analysis is not currently available. "
                "Please use /price for basic stock information."
            )
            return
        
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /analyze TSLA")
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🤖 Performing analysis for {symbol}...")
            
            analysis = await self.trading_intelligence.analyze_stock(symbol, update.effective_user.id)
            
            if 'error' in analysis:
                await update.message.reply_text(f"❌ {analysis['error']}")
            else:
                await update.message.reply_text(analysis.get('analysis', 'Analysis not available'))
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text("Sorry, there was an error performing the analysis.")
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command and natural language"""
        try:
            if context.args:
                user_message = ' '.join(context.args)
            else:
                user_message = update.message.text
            
            if not user_message:
                await update.message.reply_text("Please provide a message to chat about.")
                return
            
            response = await self.ai_service.generate_response(user_message, update.effective_user.id)
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error in chat command: {e}")
            await update.message.reply_text("Sorry, there was an error processing your message.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        await self.chat_command(update, context)
    
    async def setup_telegram_bot(self):
        """Setup Telegram bot with handlers"""
        try:
            self.application = Application.builder().token(self.telegram_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            self.application.add_handler(CommandHandler("alert", self.alert_command))
            self.application.add_handler(CommandHandler("alerts", self.alerts_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("chat", self.chat_command))
            
            # Message handler
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            logger.info("✅ Telegram bot handlers configured")
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
                    'bot': 'TradeAI_Integrated',
                    'uptime': int(time.time() - self.start_time),
                    'version': '2.0'
                })
            
            self.web_app = web.Application()
            self.web_app.router.add_get('/health', health_check)
            self.web_app.router.add_get('/', health_check)
            
            logger.info(f"✅ Health server configured on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup health server: {e}")
            return False
    
    async def run(self):
        """Run the bot"""
        try:
            logger.info("=== Starting TradeAI Integrated Bot ===")
            
            # Setup bot
            if not await self.setup_telegram_bot():
                return
            
            if not await self.setup_health_server():
                return
            
            # Start health server
            runner = web.AppRunner(self.web_app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', self.port)
            await site.start()
            logger.info(f"✅ Health server started on port {self.port}")
            
            # Start alert monitoring if available
            if hasattr(self.alert_service, 'start_monitoring'):
                asyncio.create_task(self.alert_service.start_monitoring())
                logger.info("✅ Alert monitoring started")
            
            # Start Telegram bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("✅ Telegram bot started successfully")
            
            logger.info("🚀 TradeAI Integrated Bot is operational!")
            logger.info("📊 Available features depend on service configuration")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
            
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            raise
        finally:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            if 'runner' in locals():
                await runner.cleanup()

async def main():
    """Main entry point"""
    try:
        bot = TradeAIIntegratedBot()
        await bot.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())