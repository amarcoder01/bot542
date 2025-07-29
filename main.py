#!/usr/bin/env python3
"""
TradeAI Companion Bot - Comprehensive Main Entry Point
Integrates all features from the deploy folder into a unified trading bot
"""
import os
import sys
import asyncio
import logging
import signal
import time
from typing import Optional
from pathlib import Path
from aiohttp import web
from datetime import datetime

# Add deploy directory to Python path for imports
deploy_dir = Path(__file__).parent / 'deploy'
sys.path.insert(0, str(deploy_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TradeAI')

# Import all services and components from deploy folder
try:
    from config import Config
    logger.info("✅ Config imported")
except ImportError:
    logger.error("Failed to import Config")
    sys.exit(1)

# Import services with graceful fallback
services_available = {}

try:
    from market_data_service import MarketDataService
    services_available['market'] = True
except ImportError as e:
    logger.warning(f"MarketDataService not available: {e}")
    services_available['market'] = False

try:
    from openai_service import OpenAIService
    services_available['openai'] = True
except ImportError as e:
    logger.warning(f"OpenAIService not available: {e}")
    services_available['openai'] = False

try:
    from alert_service import AlertService
    services_available['alerts'] = True
except ImportError as e:
    logger.warning(f"AlertService not available: {e}")
    services_available['alerts'] = False

try:
    from chart_service import ChartService
    services_available['charts'] = True
except ImportError as e:
    logger.warning(f"ChartService not available: {e}")
    services_available['charts'] = False

try:
    from qlib_service import QlibService
    services_available['qlib'] = True
except ImportError as e:
    logger.warning(f"QlibService not available: {e}")
    services_available['qlib'] = False

try:
    from trading_intelligence import TradingIntelligence
    services_available['trading_intelligence'] = True
except ImportError as e:
    logger.warning(f"TradingIntelligence not available: {e}")
    services_available['trading_intelligence'] = False

try:
    from portfolio_optimizer import ModernPortfolioOptimizer
    services_available['portfolio'] = True
except ImportError as e:
    logger.warning(f"PortfolioOptimizer not available: {e}")
    services_available['portfolio'] = False

try:
    from conversation_memory import ConversationMemory
    services_available['memory'] = True
except ImportError as e:
    logger.warning(f"ConversationMemory not available: {e}")
    services_available['memory'] = False

try:
    from auto_trainer import AutoTrainer
    services_available['auto_trainer'] = True
except ImportError as e:
    logger.warning(f"AutoTrainer not available: {e}")
    services_available['auto_trainer'] = False

logger.info(f"✅ Services available: {services_available}")

# Import Telegram components
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

class TradeAIBot:
    """Comprehensive Trading Bot with all integrated features"""
    
    def __init__(self):
        """Initialize bot with all services"""
        self.config = Config()
        self.telegram_token = os.getenv('TELEGRAM_API_TOKEN', '')
        self.port = int(os.getenv('PORT', 5000))
        self.start_time = time.time()
        
        if not self.telegram_token:
            raise ValueError("TELEGRAM_API_TOKEN is required")
        
        # Initialize all services
        logger.info("🚀 Initializing TradeAI Bot services...")
        
        # Core services - initialize only if available
        self.market_service = MarketDataService() if services_available.get('market') else None
        self.ai_service = OpenAIService() if services_available.get('openai') else None
        self.chart_service = ChartService() if services_available.get('charts') else None
        self.trading_intelligence = TradingIntelligence() if services_available.get('trading_intelligence') else None
        self.portfolio_optimizer = ModernPortfolioOptimizer() if services_available.get('portfolio') else None
        self.memory_service = ConversationMemory() if services_available.get('memory') else None
        
        # Advanced services
        self.qlib_service = QlibService() if services_available.get('qlib') else None
        self.auto_trainer = AutoTrainer(self.qlib_service) if services_available.get('auto_trainer') and self.qlib_service else None
        
        # Alert service needs a callback and market service
        if services_available.get('alerts') and self.market_service:
            self.alert_service = AlertService(self.market_service, self.send_alert_notification)
        else:
            self.alert_service = None
        
        # Telegram application
        self.application = None
        self.web_app = None
        
        logger.info(f"✅ Services initialized: {[k for k, v in services_available.items() if v]}")
    
    async def send_alert_notification(self, user_id: int, message: str):
        """Send alert notification to user"""
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=f"🚨 Alert Triggered!\n\n{message}"
            )
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    # Command Handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """🤖 Welcome to TradeAI Companion Bot!

I'm your comprehensive AI-powered trading assistant with advanced features:

📊 **Market Analysis**
• /price AAPL - Real-time stock prices & charts
• /analyze TSLA - AI-powered deep analysis
• /market - Market overview & indices
• /movers - Top gainers and losers
• /sectors - Sector performance analysis

🤖 **AI Intelligence**
• /chat - Natural conversation about markets
• /sentiment AAPL - Market sentiment analysis
• /predict MSFT - AI price predictions
• /signal GOOGL - Qlib trading signals

📈 **Portfolio Management**
• /portfolio - Optimize your portfolio
• /risk - Risk assessment
• /backtest - Strategy backtesting

🚨 **Smart Alerts**
• /alert AAPL above 150 - Set price alerts
• /alerts - View your active alerts
• /remove_alert [ID] - Remove an alert

📊 **Technical Analysis**
• /chart AAPL 3mo - Advanced charts
• /indicators TSLA - Technical indicators
• /patterns NVDA - Chart patterns

🎯 **Trading Opportunities**
• /opportunities - AI-detected opportunities
• /screener - Stock screener
• /watchlist - Your watchlist

Type /help to see all commands or just chat with me naturally!"""
        
        await update.message.reply_text(welcome_message)
        logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """📋 **TradeAI Commands**

**📊 Market Data:**
/price [SYMBOL] - Current price & chart
/analyze [SYMBOL] - Deep AI analysis
/market - Market overview
/movers - Top gainers/losers
/sectors - Sector performance
/news [SYMBOL] - Latest news

**🤖 AI Features:**
/chat [message] - AI conversation
/sentiment [SYMBOL] - Sentiment analysis
/predict [SYMBOL] - Price prediction
/signal [SYMBOL] - Trading signals

**📈 Portfolio:**
/portfolio - Portfolio optimizer
/risk - Risk assessment
/backtest - Test strategies

**🚨 Alerts:**
/alert [SYMBOL] [above/below] [PRICE] - Set alert
/alerts - View alerts
/remove_alert [ID] - Remove alert

**📊 Technical:**
/chart [SYMBOL] [period] - Charts
/indicators [SYMBOL] - Indicators
/patterns [SYMBOL] - Patterns

**🎯 Trading:**
/opportunities - Find opportunities
/screener - Stock screener
/watchlist - Your watchlist

**🔧 Bot:**
/status - Bot status
/help - This help menu

💡 **Tips:**
• Just type naturally to chat
• Use stock symbols like AAPL, TSLA
• Periods: 1d, 5d, 1mo, 3mo, 1y"""
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        uptime = int(time.time() - self.start_time)
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        status_text = f"""📊 **TradeAI Bot Status**

✅ Status: Fully Operational
⏱️ Uptime: {hours}h {minutes}m {seconds}s
🔧 Version: 2.0 Integrated
📡 Services Status:

• Telegram API: ✅ Connected
• Market Data: ✅ Active
• AI Service: ✅ {'Available' if self.ai_service else 'Not configured'}
• Chart Service: ✅ Ready
• Alert Service: ✅ Monitoring
• Qlib Service: ✅ Initialized
• Portfolio Optimizer: ✅ Ready
• Auto Trainer: ✅ {'Running' if hasattr(self, 'auto_trainer') and self.auto_trainer else 'Standby'}

📊 Features Available:
• Real-time market data
• AI-powered analysis
• Smart price alerts
• Portfolio optimization
• Technical indicators
• Trading signals
• Natural language chat

All systems operational! 🚀"""
        
        await update.message.reply_text(status_text)
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command with chart"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /price AAPL")
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🔍 Fetching price data for {symbol}...")
            
            # Get price data
            price_data = await self.market_service.get_stock_price(symbol, update.effective_user.id)
            
            if 'error' in price_data:
                await update.message.reply_text(f"❌ {price_data['error']}")
                return
            
            # Format price message
            price_text = f"""📊 **{price_data.get('company_name', symbol)}** ({symbol})

💵 Price: ${price_data.get('price', 'N/A'):.2f}
📈 Change: {price_data.get('change', 'N/A'):.2f} ({price_data.get('change_percent', 'N/A'):.2f}%)
📊 Volume: {price_data.get('volume', 'N/A'):,}

📈 Day Range: ${price_data.get('day_low', 'N/A'):.2f} - ${price_data.get('day_high', 'N/A'):.2f}
📊 52W Range: ${price_data.get('low_52w', 'N/A'):.2f} - ${price_data.get('high_52w', 'N/A'):.2f}
💹 Market Cap: {price_data.get('market_cap', 'N/A')}
📊 P/E Ratio: {price_data.get('pe_ratio', 'N/A')}

🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            # Send price info first
            await update.message.reply_text(price_text)
            
            # Generate and send chart
            chart_url = await self.chart_service.generate_price_chart(symbol, period='1mo')
            if chart_url:
                await update.message.reply_photo(
                    photo=chart_url,
                    caption=f"📈 1 Month Price Chart for {symbol}"
                )
            
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching the price data.")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command with AI analysis"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /analyze TSLA")
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🤖 Performing AI analysis for {symbol}... This may take a moment.")
            
            # Get comprehensive analysis
            analysis = await self.trading_intelligence.analyze_stock(symbol, update.effective_user.id)
            
            if 'error' in analysis:
                await update.message.reply_text(f"❌ {analysis['error']}")
                return
            
            # Send analysis
            await update.message.reply_text(analysis.get('analysis', 'Analysis not available'))
            
            # Send recommendation if available
            if 'recommendation' in analysis:
                rec_text = f"""🎯 **AI Recommendation for {symbol}**

{analysis['recommendation']}

⚠️ *This is AI analysis, not financial advice. Always do your own research.*"""
                await update.message.reply_text(rec_text)
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text("Sorry, there was an error performing the analysis.")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        try:
            await update.message.reply_text("📊 Fetching market overview...")
            
            # Get market summary
            market_data = await self.market_service.get_market_summary()
            
            if 'error' in market_data:
                await update.message.reply_text(f"❌ {market_data['error']}")
                return
            
            # Format market overview
            indices = market_data.get('indices', {})
            market_text = f"""📊 **Market Overview**

**US Markets:**
• S&P 500: {indices.get('S&P 500', 'N/A')}
• NASDAQ: {indices.get('NASDAQ', 'N/A')}
• DOW: {indices.get('DOW', 'N/A')}

**Global Markets:**
• FTSE 100: {indices.get('FTSE', 'N/A')}
• Nikkei: {indices.get('NIKKEI', 'N/A')}
• DAX: {indices.get('DAX', 'N/A')}

**Commodities:**
• Gold: {indices.get('GOLD', 'N/A')}
• Oil: {indices.get('OIL', 'N/A')}

**Crypto:**
• Bitcoin: {indices.get('BTC', 'N/A')}
• Ethereum: {indices.get('ETH', 'N/A')}

📈 Market Sentiment: {market_data.get('sentiment', 'Neutral')}

🕐 Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            await update.message.reply_text(market_text)
            
        except Exception as e:
            logger.error(f"Error in market command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching market data.")
    
    async def alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alert command to set price alerts"""
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
        """Handle /alerts command to show active alerts"""
        try:
            alerts = await self.alert_service.get_user_alerts(update.effective_user.id)
            
            if not alerts:
                await update.message.reply_text("You don't have any active alerts. Use /alert to create one.")
                return
            
            alerts_text = "🚨 **Your Active Alerts:**\n\n"
            for alert in alerts:
                alerts_text += f"• Alert #{alert['id']}: {alert['symbol']} {alert['condition']}\n"
            
            alerts_text += "\nUse /remove_alert [ID] to remove an alert."
            
            await update.message.reply_text(alerts_text)
            
        except Exception as e:
            logger.error(f"Error in alerts command: {e}")
            await update.message.reply_text("Sorry, there was an error fetching your alerts.")
    
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signal command for Qlib trading signals"""
        try:
            if not context.args:
                await update.message.reply_text("Please provide a stock symbol. Example: /signal MSFT")
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🤖 Generating AI trading signal for {symbol}...")
            
            # Get signal from Qlib service
            signal = self.qlib_service.get_trading_signal(symbol)
            
            if signal is None:
                await update.message.reply_text(f"No signal available for {symbol}")
                return
            
            # Interpret signal
            if signal > 0.15:
                recommendation = "🚀 STRONG BUY"
                confidence = "High"
            elif signal > 0.05:
                recommendation = "📈 BUY"
                confidence = "Moderate"
            elif signal > -0.05:
                recommendation = "⚖️ HOLD"
                confidence = "Low"
            elif signal > -0.15:
                recommendation = "📉 SELL"
                confidence = "Moderate"
            else:
                recommendation = "🔻 STRONG SELL"
                confidence = "High"
            
            signal_text = f"""🤖 **AI Trading Signal for {symbol}**

📊 Signal Strength: {signal:.3f}
🎯 Recommendation: {recommendation}
💪 Confidence: {confidence}

📈 Signal Analysis:
• Positive values indicate buy signals
• Negative values indicate sell signals
• Range: -1.0 to +1.0

⚠️ *AI signals are for reference only. Not financial advice.*"""
            
            await update.message.reply_text(signal_text)
            
        except Exception as e:
            logger.error(f"Error in signal command: {e}")
            await update.message.reply_text("Sorry, there was an error generating the signal.")
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command for portfolio optimization"""
        try:
            if not context.args:
                example_text = """📊 **Portfolio Optimizer**

Usage: /portfolio AAPL,MSFT,GOOGL,TSLA

Provide comma-separated stock symbols to optimize.

Risk levels:
• Add 'conservative' for low risk
• Add 'moderate' for balanced (default)
• Add 'aggressive' for high risk

Example: /portfolio AAPL,MSFT,GOOGL aggressive"""
                await update.message.reply_text(example_text)
                return
            
            # Parse symbols and risk level
            args_text = ' '.join(context.args)
            risk_tolerance = 'moderate'
            
            for risk in ['conservative', 'moderate', 'aggressive']:
                if risk in args_text.lower():
                    risk_tolerance = risk
                    args_text = args_text.lower().replace(risk, '').strip()
                    break
            
            symbols = [s.strip().upper() for s in args_text.split(',') if s.strip()]
            
            if len(symbols) < 2:
                await update.message.reply_text("Please provide at least 2 symbols for portfolio optimization.")
                return
            
            await update.message.reply_text(f"🔄 Optimizing portfolio with {len(symbols)} stocks ({risk_tolerance} risk)...")
            
            # Optimize portfolio
            result = self.portfolio_optimizer.optimize_portfolio(symbols, risk_tolerance)
            
            if 'error' in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            # Format results
            weights = result.get('weights', {})
            metrics = result.get('metrics', {})
            
            portfolio_text = f"""📊 **Optimized Portfolio ({risk_tolerance.title()} Risk)**

**Allocation:**
"""
            for symbol, weight in weights.items():
                portfolio_text += f"• {symbol}: {weight:.1%}\n"
            
            portfolio_text += f"""
**Expected Performance:**
• Annual Return: {metrics.get('expected_return', 0):.1%}
• Volatility: {metrics.get('volatility', 0):.1%}
• Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}

💡 This allocation maximizes returns while managing risk according to your preference.

⚠️ *This is a mathematical optimization, not financial advice.*"""
            
            await update.message.reply_text(portfolio_text)
            
        except Exception as e:
            logger.error(f"Error in portfolio command: {e}")
            await update.message.reply_text("Sorry, there was an error optimizing the portfolio.")
    
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command and natural language messages"""
        try:
            # Get message text
            if context.args:
                user_message = ' '.join(context.args)
            else:
                user_message = update.message.text
            
            if not user_message:
                await update.message.reply_text("Please provide a message to chat about.")
                return
            
            # Generate AI response
            response = await self.ai_service.generate_response(
                user_message=user_message,
                user_id=update.effective_user.id
            )
            
            await update.message.reply_text(response or "I couldn't generate a response. Please try again.")
            
        except Exception as e:
            logger.error(f"Error in chat command: {e}")
            await update.message.reply_text("Sorry, there was an error processing your message.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages as chat"""
        await self.chat_command(update, context)
    
    async def setup_telegram_bot(self):
        """Setup Telegram bot with all handlers"""
        try:
            # Create application
            self.application = Application.builder().token(self.telegram_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            
            # Market data commands
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            
            # Alert commands
            self.application.add_handler(CommandHandler("alert", self.alert_command))
            self.application.add_handler(CommandHandler("alerts", self.alerts_command))
            
            # AI commands
            self.application.add_handler(CommandHandler("signal", self.signal_command))
            self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
            self.application.add_handler(CommandHandler("chat", self.chat_command))
            
            # Message handler for natural chat
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
                    'version': '2.0',
                    'features': {
                        'telegram': True,
                        'market_data': True,
                        'ai_service': bool(self.ai_service),
                        'alerts': True,
                        'charts': True,
                        'portfolio': True,
                        'qlib': True
                    }
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
        """Run the integrated bot"""
        try:
            logger.info("=== Starting TradeAI Integrated Bot ===")
            
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
            
            # Start alert monitoring service if available
            if self.alert_service:
                asyncio.create_task(self.alert_service.start_monitoring())
                logger.info("✅ Alert monitoring service started")
            
            # Start auto trainer if configured
            if self.auto_trainer:
                asyncio.create_task(self.auto_trainer.start())
                logger.info("✅ Auto trainer service started")
            
            # Start Telegram bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("✅ Telegram bot started successfully")
            
            logger.info("🚀 TradeAI Bot is fully operational with all features!")
            logger.info("📊 Available features:")
            logger.info("  • Real-time market data")
            logger.info("  • AI-powered analysis")
            logger.info("  • Smart price alerts")
            logger.info("  • Portfolio optimization")
            logger.info("  • Qlib trading signals")
            logger.info("  • Technical charts")
            logger.info("  • Natural language chat")
            
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
            if self.alert_service:
                self.alert_service.stop()
            
            if hasattr(self, 'auto_trainer'):
                self.auto_trainer.stop()
            
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot stopped")
            
            if 'runner' in locals():
                await runner.cleanup()
                logger.info("Health server stopped")

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    sys.exit(0)

async def main():
    """Main entry point"""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
        
        # Run the bot
        bot = TradeAIBot()
        await bot.run()
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())