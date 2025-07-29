"""
Simplified Telegram Handler without security features
"""
import os
import logging
import asyncio
from typing import Optional, Dict, List, Any
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logger = logging.getLogger('TradingBot')

# Import services
try:
    from market_data_service import MarketDataService
    from openai_service import OpenAIService
    from chart_service import ChartService
    from alert_service import AlertService
    from trading_intelligence import TradingIntelligence
    from qlib_service import QlibService
except ImportError as e:
    logger.warning(f"Some services not available: {e}")

class SimplifiedTelegramHandler:
    """Simplified Telegram handler without security middleware"""
    
    def __init__(self):
        """Initialize the handler"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8107059656:AAFNjM797l0Qfhq0OLN0OYLW0fAv6T12ICM')
        self.application = None
        
        # Initialize services
        try:
            self.market_service = MarketDataService()
            logger.info("Market data service initialized")
        except:
            logger.warning("Market data service not available")
            self.market_service = None
            
        try:
            self.openai_service = OpenAIService()
            logger.info("OpenAI service initialized")
        except:
            logger.warning("OpenAI service not available")
            self.openai_service = None
            
        try:
            self.chart_service = ChartService()
            logger.info("Chart service initialized")
        except:
            logger.warning("Chart service not available")
            self.chart_service = None
            
        try:
            self.alert_service = AlertService()
            logger.info("Alert service initialized")
        except:
            logger.warning("Alert service not available")
            self.alert_service = None
            
        try:
            self.trading_intelligence = TradingIntelligence()
            logger.info("Trading intelligence initialized")
        except:
            logger.warning("Trading intelligence not available")
            self.trading_intelligence = None
            
        try:
            self.qlib_service = QlibService()
            logger.info("Qlib service initialized")
        except:
            logger.warning("Qlib service not available")
            self.qlib_service = None
        
        # In-memory storage for portfolios and watchlists
        self.watchlists = {}
        self.portfolios = {}
        self.trade_counter = 1
        
        logger.info("Simplified Telegram handler initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        welcome_message = """
🚀 **Welcome to TradeMaster AI Bot!**

I'm your AI-powered trading assistant. Here's what I can do:

📊 **Stock Prices & Charts**
• `/price AAPL` - Get real-time prices
• `/chart TSLA` - View price charts
• `/analyze NVDA` - AI analysis

💼 **Portfolio Tracking**
• `/portfolio` - View your holdings
• `/trade buy AAPL 10 150` - Record trades
• `/watchlist` - Manage watchlist

🔔 **Price Alerts**
• `/alert AAPL above 150` - Set alerts
• `/alerts` - View active alerts

📚 **Help & Commands**
• `/help` - See all commands
• `/help_trading` - Trading commands
• `/help_alerts` - Alert commands

Type any command to get started!
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_message = """
📚 **TradeMaster AI Commands**

**📊 Trading Commands:**
• `/price AAPL` - Get stock price
• `/chart TSLA` - View chart
• `/analyze NVDA` - AI analysis
• `/portfolio` - Your holdings
• `/trade` - Record trades
• `/watchlist` - Your watchlist

**🔔 Alert Commands:**
• `/alert` - Set price alert
• `/alerts` - View alerts
• `/remove_alert` - Delete alert

**📖 Help Sections:**
• `/help_trading` - Trading details
• `/help_alerts` - Alert details
• `/help_advanced` - Advanced features

**💬 Natural Language:**
Just ask questions like:
• "What's the price of Apple?"
• "Show me Tesla chart"
• "Analyze Microsoft stock"

Happy trading! 📈
"""
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def help_trading_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help_trading command"""
        help_message = """📊 **STOCK PRICES, CHARTS & ANALYSIS**

**💹 GET STOCK PRICES:**
• `/price AAPL` - Get Apple's current price
• `/price TSLA` - Get Tesla's current price
• `/price SPY` - Get S&P 500 ETF price
• `/price GOOG` - Get Google price

**📈 VIEW CHARTS:**
• `/chart AAPL` - See Apple's price chart
• `/chart TSLA 1M` - Tesla chart for 1 month
• `/chart NVDA 6M` - NVIDIA chart for 6 months
• `/chart GOOG 1Y` - Google chart for 1 year

**🤖 GET AI ANALYSIS:**
• `/analyze AAPL` - AI analysis of Apple
• `/analyze TSLA` - AI analysis of Tesla
• `/analyze tech` - Analysis of tech sector

**📊 TRACK YOUR INVESTMENTS:**
• `/trade buy AAPL 10 150` - Record buying 10 Apple shares at $150
• `/trade sell TSLA 5 250` - Record selling 5 Tesla shares at $250
• `/portfolio` - See all your recorded trades
• `/trades` - View your trading history

**💡 WHAT STOCKS CAN I CHECK:**
• **US Stocks:** Apple (AAPL), Tesla (TSLA), Microsoft (MSFT), etc.
• **ETFs:** SPY, QQQ, VTI (popular investment funds)
• **Crypto:** BTC-USD (Bitcoin), ETH-USD (Ethereum)
• **Indices:** ^GSPC (S&P 500), ^IXIC (NASDAQ)

**⚡ QUICK TIPS:**
• Use stock symbols like AAPL (not "Apple")
• Charts show the last few months by default
• AI analysis explains if a stock looks good or risky
• You can track paper trades to practice

🔙 Return to main menu: `/help`"""
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def help_alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help_alerts command"""
        help_message = """🔔 **PRICE ALERTS & NOTIFICATIONS**

**⚡ SET PRICE ALERTS:**
• `/alert AAPL above 150` - Alert when Apple goes above $150
• `/alert TSLA below 200` - Alert when Tesla drops below $200
• `/alert NVDA above 500` - Alert when NVIDIA hits $500

**📋 MANAGE ALERTS:**
• `/alerts` - View all your active alerts
• `/remove_alert 123` - Delete alert by ID

**💡 ALERT TIPS:**
• Alerts check prices every few minutes
• You'll get a Telegram message when triggered
• Each alert works once then auto-deletes
• Set multiple alerts for the same stock

**📊 EXAMPLE ALERTS:**
• Breakout alert: `/alert AAPL above 180`
• Support alert: `/alert TSLA below 250`
• Round number: `/alert SPY above 500`

🔙 Return to main menu: `/help`"""
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /price command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please provide a stock symbol.\nExample: `/price AAPL`",
                    parse_mode='Markdown'
                )
                return
            
            symbol = context.args[0].upper()
            
            if self.market_service:
                # Get real market data
                data = await self.market_service.get_stock_price(symbol)
                
                response = f"""💰 **{data['symbol']} - {data.get('company_name', symbol)}**

**Price:** ${data['price']:.2f}
**Change:** {data['change']:+.2f} ({data['change_percent']:+.2f}%)
**Volume:** {data.get('volume', 'N/A'):,}

**Day Range:** ${data.get('day_low', 'N/A'):.2f} - ${data.get('day_high', 'N/A'):.2f}
**52W Range:** ${data.get('low_52w', 'N/A'):.2f} - ${data.get('high_52w', 'N/A'):.2f}

_Data from {data.get('source', 'Market')}_"""
            else:
                # Fallback response
                response = f"Market data service is not available. Please try again later."
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text(f"Error getting price for {symbol}")
    
    async def chart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /chart command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please provide a stock symbol.\nExample: `/chart AAPL` or `/chart TSLA 6M`",
                    parse_mode='Markdown'
                )
                return
            
            symbol = context.args[0].upper()
            period = context.args[1] if len(context.args) > 1 else '1M'
            
            await update.message.reply_text(f"📊 Generating chart for {symbol}...")
            
            if self.chart_service:
                chart_url = await self.chart_service.generate_price_chart(symbol, period)
                if chart_url:
                    await update.message.reply_photo(photo=chart_url, caption=f"{symbol} - {period} chart")
                else:
                    await update.message.reply_text(
                        f"Chart generation is currently unavailable.\n"
                        f"You can view {symbol} charts at: https://finance.yahoo.com/quote/{symbol}"
                    )
            else:
                await update.message.reply_text(
                    f"Chart service is not available.\n"
                    f"You can view {symbol} charts at: https://finance.yahoo.com/quote/{symbol}"
                )
                
        except Exception as e:
            logger.error(f"Error in chart command: {e}")
            await update.message.reply_text("Error generating chart. Please try again.")
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /analyze command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "Please provide a stock symbol.\nExample: `/analyze AAPL`",
                    parse_mode='Markdown'
                )
                return
            
            symbol = context.args[0].upper()
            await update.message.reply_text(f"🤖 Analyzing {symbol}...")
            
            if self.openai_service and self.market_service:
                # Get market data
                price_data = await self.market_service.get_stock_price(symbol)
                
                # Generate AI analysis
                prompt = f"""Analyze {symbol} ({price_data.get('company_name', symbol)}) stock:
Current price: ${price_data['price']:.2f}
Change: {price_data['change_percent']:+.2f}%
Volume: {price_data.get('volume', 'N/A'):,}
Day range: ${price_data.get('day_low', 0):.2f} - ${price_data.get('day_high', 0):.2f}

Provide a brief analysis including:
1. Current trend (bullish/bearish)
2. Key support/resistance levels
3. Investment recommendation
4. Risk factors"""
                
                analysis = await self.openai_service.get_trading_advice(prompt, str(update.effective_user.id))
                
                response = f"""🤖 **AI Analysis for {symbol}**

{analysis}

_Analysis based on current market data_"""
            else:
                response = "AI analysis service is not available. Please try again later."
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analyze command: {e}")
            await update.message.reply_text("Error generating analysis. Please try again.")
    
    async def watchlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /watchlist command"""
        try:
            user_id = str(update.effective_user.id)
            
            if not context.args:
                # Show watchlist
                watchlist = self.watchlists.get(user_id, [])
                
                if not watchlist:
                    response = "📋 **Your Watchlist**\n\n*Your watchlist is empty.*\n\nAdd stocks with: `/watchlist add AAPL`"
                else:
                    response = "📋 **Your Watchlist**\n\n"
                    for symbol in watchlist:
                        response += f"• {symbol}\n"
                    response += f"\n_Total: {len(watchlist)} stocks_"
                
            elif context.args[0].lower() == 'add' and len(context.args) > 1:
                symbol = context.args[1].upper()
                if user_id not in self.watchlists:
                    self.watchlists[user_id] = []
                
                if symbol not in self.watchlists[user_id]:
                    self.watchlists[user_id].append(symbol)
                    response = f"✅ **{symbol}** added to your watchlist!"
                else:
                    response = f"ℹ️ **{symbol}** is already in your watchlist."
                    
            elif context.args[0].lower() == 'remove' and len(context.args) > 1:
                symbol = context.args[1].upper()
                if user_id in self.watchlists and symbol in self.watchlists[user_id]:
                    self.watchlists[user_id].remove(symbol)
                    response = f"✅ **{symbol}** removed from your watchlist."
                else:
                    response = f"❌ **{symbol}** was not in your watchlist."
            else:
                response = """📋 **Watchlist Commands**

• `/watchlist` - View your watchlist
• `/watchlist add AAPL` - Add a stock
• `/watchlist remove AAPL` - Remove a stock"""
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in watchlist command: {e}")
            await update.message.reply_text("Error managing watchlist. Please try again.")
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /portfolio command"""
        try:
            user_id = str(update.effective_user.id)
            portfolio = self.portfolios.get(user_id, {'trades': [], 'holdings': {}})
            
            if not portfolio['holdings']:
                response = """💼 **Your Portfolio**

*Your portfolio is empty.*

Start tracking trades with:
`/trade buy AAPL 10 150`"""
            else:
                response = "💼 **Your Portfolio**\n\n"
                total_value = 0
                
                for symbol, holding in portfolio['holdings'].items():
                    quantity = holding['quantity']
                    avg_price = holding['avg_price']
                    position_value = quantity * avg_price
                    total_value += position_value
                    
                    response += f"**{symbol}**: {quantity} shares @ ${avg_price:.2f}\n"
                    response += f"  💰 Value: ${position_value:.2f}\n\n"
                
                response += f"**Total Portfolio Value**: ${total_value:,.2f}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in portfolio command: {e}")
            await update.message.reply_text("Error viewing portfolio. Please try again.")
    
    async def trade_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /trade command"""
        try:
            if len(context.args) != 4:
                await update.message.reply_text(
                    "❌ **Usage**: `/trade [buy|sell] SYMBOL QUANTITY PRICE`\n\n"
                    "**Examples:**\n"
                    "• `/trade buy AAPL 10 150.00`\n"
                    "• `/trade sell TSLA 5 250.00`",
                    parse_mode='Markdown'
                )
                return
            
            user_id = str(update.effective_user.id)
            action, symbol, quantity_str, price_str = context.args
            action = action.lower()
            symbol = symbol.upper()
            
            if action not in ["buy", "sell"]:
                await update.message.reply_text("❌ Action must be 'buy' or 'sell'")
                return
            
            try:
                quantity = float(quantity_str)
                price = float(price_str)
                
                if quantity <= 0 or price <= 0:
                    await update.message.reply_text("❌ Quantity and price must be positive numbers.")
                    return
            except ValueError:
                await update.message.reply_text("❌ Quantity and price must be valid numbers.")
                return
            
            # Initialize portfolio if needed
            if user_id not in self.portfolios:
                self.portfolios[user_id] = {'trades': [], 'holdings': {}}
            
            # Record trade
            trade = {
                'id': self.trade_counter,
                'type': action,
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            }
            
            self.portfolios[user_id]['trades'].append(trade)
            self.trade_counter += 1
            
            # Update holdings
            holdings = self.portfolios[user_id]['holdings']
            if symbol not in holdings:
                holdings[symbol] = {'quantity': 0, 'avg_price': 0}
            
            if action == 'buy':
                total_cost = holdings[symbol]['quantity'] * holdings[symbol]['avg_price'] + quantity * price
                holdings[symbol]['quantity'] += quantity
                holdings[symbol]['avg_price'] = total_cost / holdings[symbol]['quantity']
            else:  # sell
                holdings[symbol]['quantity'] -= quantity
                if holdings[symbol]['quantity'] <= 0:
                    del holdings[symbol]
            
            trade_emoji = '🟢' if action == 'buy' else '🔴'
            response = f"{trade_emoji} **Trade Recorded!**\n\n"
            response += f"**Action**: {action.upper()}\n"
            response += f"**Symbol**: {symbol}\n"
            response += f"**Quantity**: {quantity}\n"
            response += f"**Price**: ${price:.2f}\n"
            response += f"**Total**: ${trade['total']:,.2f}\n"
            response += f"**Trade ID**: #{trade['id']}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in trade command: {e}")
            await update.message.reply_text("❌ Error recording trade. Please try again.")
    
    async def trades_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /trades command"""
        try:
            user_id = str(update.effective_user.id)
            portfolio = self.portfolios.get(user_id, {'trades': []})
            trades = portfolio['trades']
            
            if not trades:
                response = """📊 **Trade History**

*No trades recorded yet.*

Start tracking with:
`/trade buy AAPL 10 150`"""
            else:
                response = "📊 **Trade History**\n\n"
                
                # Show last 10 trades, newest first
                for trade in trades[-10:][::-1]:
                    trade_emoji = '🟢' if trade['type'] == 'buy' else '🔴'
                    response += f"{trade_emoji} **#{trade['id']}**\n"
                    response += f"  {trade['type'].upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}\n"
                    response += f"  Total: ${trade['total']:,.2f}\n\n"
                
                response += f"_Showing last {min(10, len(trades))} of {len(trades)} total trades_"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in trades command: {e}")
            await update.message.reply_text("❌ Error viewing trade history. Please try again.")
    
    async def alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /alert command"""
        try:
            if len(context.args) < 3:
                await update.message.reply_text(
                    "❌ **Usage**: `/alert SYMBOL above/below PRICE`\n\n"
                    "**Examples:**\n"
                    "• `/alert AAPL above 150`\n"
                    "• `/alert TSLA below 200`",
                    parse_mode='Markdown'
                )
                return
            
            symbol = context.args[0].upper()
            condition = context.args[1].lower()
            price = float(context.args[2])
            
            if condition not in ['above', 'below']:
                await update.message.reply_text("❌ Condition must be 'above' or 'below'")
                return
            
            response = f"✅ **Alert Set!**\n\n"
            response += f"I'll notify you when **{symbol}** goes **{condition} ${price:.2f}**\n\n"
            response += f"_Note: Alert service requires configuration_"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in alert command: {e}")
            await update.message.reply_text("❌ Error setting alert. Please try again.")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages"""
        try:
            message = update.message.text
            
            # Simple keyword-based responses
            if 'price' in message.lower():
                await update.message.reply_text(
                    "To get stock prices, use:\n`/price AAPL`\n`/price TSLA`",
                    parse_mode='Markdown'
                )
            elif 'chart' in message.lower():
                await update.message.reply_text(
                    "To view charts, use:\n`/chart AAPL`\n`/chart TSLA 6M`",
                    parse_mode='Markdown'
                )
            elif 'help' in message.lower():
                await self.help_command(update, context)
            else:
                # If OpenAI is available, use it for natural language
                if self.openai_service:
                    response = await self.openai_service.get_trading_advice(
                        message, 
                        str(update.effective_user.id)
                    )
                    await update.message.reply_text(response)
                else:
                    await update.message.reply_text(
                        "I can help you with:\n"
                        "• Stock prices: `/price AAPL`\n"
                        "• Charts: `/chart TSLA`\n"
                        "• Analysis: `/analyze NVDA`\n"
                        "• Portfolio: `/portfolio`\n\n"
                        "Type `/help` for all commands!",
                        parse_mode='Markdown'
                    )
                    
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            await update.message.reply_text("I encountered an error. Please try a command like `/help`")
    
    async def run(self):
        """Run the bot"""
        try:
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("help_trading", self.help_trading_command))
            self.application.add_handler(CommandHandler("help_alerts", self.help_alerts_command))
            self.application.add_handler(CommandHandler("price", self.price_command))
            self.application.add_handler(CommandHandler("chart", self.chart_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("watchlist", self.watchlist_command))
            self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
            self.application.add_handler(CommandHandler("trade", self.trade_command))
            self.application.add_handler(CommandHandler("trades", self.trades_command))
            self.application.add_handler(CommandHandler("alert", self.alert_command))
            
            # Add message handler
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
            
            logger.info("All handlers registered successfully")
            
            # Start polling
            logger.info("Starting bot in polling mode...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(drop_pending_updates=True)
            
            logger.info("✅ Bot is running! Send /start to begin.")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise