"""
Patches for trading commands to work with fallback services
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger('CommandPatches')

async def patched_watchlist_command(handler, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Patched watchlist command that works without database"""
    try:
        user_id = update.effective_user.id
        
        # Use fallback watchlist service
        if hasattr(handler, 'watchlist_service'):
            watchlist_service = handler.watchlist_service
        else:
            from service_wrappers import FallbackWatchlistService
            watchlist_service = FallbackWatchlistService()
            handler.watchlist_service = watchlist_service
        
        # Parse command arguments
        if not context.args:
            # Show watchlist
            symbols = await watchlist_service.get_user_watchlist(user_id)
            
            if not symbols:
                response = "📋 **Your Watchlist**\n\n*Your watchlist is empty.*\n\nAdd stocks with: `/watchlist add AAPL`"
            else:
                response = "📋 **Your Watchlist**\n\n"
                
                # Get price data for each symbol
                for symbol in symbols:
                    try:
                        price_data = await handler.market_service.get_stock_price(symbol, user_id)
                        price = price_data.get('price', 0)
                        change = price_data.get('change_percent', 0)
                        change_emoji = '📈' if change >= 0 else '📉'
                        
                        response += f"{change_emoji} **{symbol}**: ${price:.2f} ({change:+.2f}%)\n"
                    except:
                        response += f"• **{symbol}**: Price unavailable\n"
                
                response += f"\n_Total: {len(symbols)} stocks_"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        elif context.args[0].lower() == 'add' and len(context.args) > 1:
            # Add to watchlist
            symbol = context.args[1].upper()
            success = await watchlist_service.add_to_watchlist(user_id, symbol)
            
            if success:
                await update.message.reply_text(
                    f"✅ **{symbol}** added to your watchlist!\n\nView with: `/watchlist`",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"ℹ️ **{symbol}** is already in your watchlist.",
                    parse_mode='Markdown'
                )
                
        elif context.args[0].lower() == 'remove' and len(context.args) > 1:
            # Remove from watchlist
            symbol = context.args[1].upper()
            success = await watchlist_service.remove_from_watchlist(user_id, symbol)
            
            if success:
                await update.message.reply_text(
                    f"✅ **{symbol}** removed from your watchlist.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ **{symbol}** was not in your watchlist.",
                    parse_mode='Markdown'
                )
        else:
            # Show help
            help_text = """📋 **Watchlist Commands**

• `/watchlist` - View your watchlist
• `/watchlist add AAPL` - Add a stock
• `/watchlist remove AAPL` - Remove a stock

Monitor your favorite stocks easily!"""
            await update.message.reply_text(help_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in patched watchlist command: {e}")
        await update.message.reply_text("❌ Error managing watchlist. Please try again.")

async def patched_portfolio_command(handler, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Patched portfolio command that works without database"""
    try:
        user_id = update.effective_user.id
        
        # Use fallback portfolio service
        if hasattr(handler, 'portfolio_service'):
            portfolio_service = handler.portfolio_service
        else:
            from service_wrappers import FallbackPortfolioService
            portfolio_service = FallbackPortfolioService()
            handler.portfolio_service = portfolio_service
        
        portfolio = await portfolio_service.get_portfolio(user_id)
        
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
                
                # Try to get current price
                try:
                    price_data = await handler.market_service.get_stock_price(symbol, user_id)
                    current_price = price_data.get('price', avg_price)
                    current_value = quantity * current_price
                    pnl = current_value - position_value
                    pnl_percent = (pnl / position_value * 100) if position_value > 0 else 0
                    
                    response += f"**{symbol}**: {quantity} shares @ ${avg_price:.2f}\n"
                    response += f"  💰 Current: ${current_value:.2f} ({pnl_percent:+.2f}%)\n\n"
                except:
                    response += f"**{symbol}**: {quantity} shares @ ${avg_price:.2f}\n\n"
            
            response += f"**Total Portfolio Value**: ${total_value:,.2f}"
            
            # Show recent trades
            if portfolio['trades']:
                response += "\n\n📊 **Recent Trades:**\n"
                for trade in portfolio['trades'][-3:]:  # Last 3 trades
                    trade_emoji = '🟢' if trade['type'] == 'buy' else '🔴'
                    response += f"{trade_emoji} {trade['type'].upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in patched portfolio command: {e}")
        await update.message.reply_text("❌ Error viewing portfolio. Please try again.")

async def patched_trade_command(handler, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Patched trade command that works without database"""
    try:
        user_id = update.effective_user.id
        args = context.args
        
        if len(args) != 4:
            await update.message.reply_text(
                "❌ **Usage**: `/trade [buy|sell] SYMBOL QUANTITY PRICE`\n\n"
                "**Examples:**\n"
                "• `/trade buy AAPL 10 150.00`\n"
                "• `/trade sell TSLA 5 250.00`",
                parse_mode='Markdown'
            )
            return
        
        action, symbol, quantity_str, price_str = args
        action = action.lower()
        symbol = symbol.upper()
        
        # Validate action
        if action not in ["buy", "sell"]:
            await update.message.reply_text("❌ Action must be 'buy' or 'sell'")
            return
        
        # Validate numbers
        try:
            quantity = float(quantity_str)
            price = float(price_str)
            
            if quantity <= 0 or price <= 0:
                await update.message.reply_text("❌ Quantity and price must be positive numbers.")
                return
        except ValueError:
            await update.message.reply_text("❌ Quantity and price must be valid numbers.")
            return
        
        # Use fallback portfolio service for trades
        if hasattr(handler, 'trade_service'):
            trade_service = handler.trade_service
        elif hasattr(handler, 'portfolio_service'):
            trade_service = handler.portfolio_service
        else:
            from service_wrappers import FallbackPortfolioService
            trade_service = FallbackPortfolioService()
            handler.trade_service = trade_service
        
        # Record the trade (handle different service types)
        if hasattr(trade_service, 'record_trade'):
            # FallbackPortfolioService
            result = await trade_service.record_trade(user_id, action, symbol, quantity, price)
        elif hasattr(trade_service, 'create_trade'):
            # TradeService from deploy folder
            result = await trade_service.create_trade(user_id, symbol, action, quantity, price)
        else:
            logger.error(f"Trade service has neither record_trade nor create_trade method")
            await update.message.reply_text("❌ Trade service configuration error. Please contact support.")
            return
        
        if result.get('success', False):
            total_value = quantity * price
            trade_emoji = '🟢' if action == 'buy' else '🔴'
            
            response = f"{trade_emoji} **Trade Recorded!**\n\n"
            response += f"**Action**: {action.upper()}\n"
            response += f"**Symbol**: {symbol}\n"
            response += f"**Quantity**: {quantity}\n"
            response += f"**Price**: ${price:.2f}\n"
            response += f"**Total**: ${total_value:,.2f}\n"
            response += f"**Trade ID**: #{result['trade_id']}\n\n"
            response += "View portfolio: `/portfolio`"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Error recording trade. Please try again.")
            
    except Exception as e:
        logger.error(f"Error in patched trade command: {e}")
        await update.message.reply_text("❌ Error recording trade. Please try again.")

async def patched_trades_command(handler, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Patched trades command that shows trade history"""
    try:
        user_id = update.effective_user.id
        
        # Use fallback portfolio service
        if hasattr(handler, 'portfolio_service'):
            portfolio_service = handler.portfolio_service
        else:
            from service_wrappers import FallbackPortfolioService
            portfolio_service = FallbackPortfolioService()
            handler.portfolio_service = portfolio_service
        
        trades = await portfolio_service.get_trades(user_id)
        
        if not trades:
            response = """📊 **Trade History**

*No trades recorded yet.*

Start tracking with:
`/trade buy AAPL 10 150`"""
        else:
            response = "📊 **Trade History**\n\n"
            
            # Show last 10 trades
            for trade in trades[-10:][::-1]:  # Reverse to show newest first
                trade_emoji = '🟢' if trade['type'] == 'buy' else '🔴'
                timestamp = trade['timestamp'].split('T')[0]  # Just date
                
                response += f"{trade_emoji} **#{trade['id']}** - {timestamp}\n"
                response += f"  {trade['type'].upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f} = ${trade['total']:,.2f}\n\n"
            
            response += f"_Showing last {min(10, len(trades))} of {len(trades)} total trades_"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in patched trades command: {e}")
        await update.message.reply_text("❌ Error viewing trade history. Please try again.")

def patch_trading_commands(handler):
    """Patch all trading commands to work with fallback services"""
    # Store original handlers
    handler._original_watchlist = getattr(handler, 'watchlist_command', None)
    handler._original_portfolio = getattr(handler, 'portfolio_command', None)
    handler._original_trade = getattr(handler, 'trade_command', None)
    handler._original_trades = getattr(handler, 'trades_command', None)
    handler._original_help_trading = getattr(handler, 'help_trading_command', None)
    handler._original_help_alerts = getattr(handler, 'help_alerts_command', None)
    handler._original_help_advanced = getattr(handler, 'help_advanced_command', None)
    handler._original_help_examples = getattr(handler, 'help_examples_command', None)
    
    # Create wrapper functions
    async def watchlist_wrapper(update, context):
        await patched_watchlist_command(handler, update, context)
    
    async def portfolio_wrapper(update, context):
        await patched_portfolio_command(handler, update, context)
    
    async def trade_wrapper(update, context):
        await patched_trade_command(handler, update, context)
    
    async def trades_wrapper(update, context):
        await patched_trades_command(handler, update, context)
    
    # Simple help_trading wrapper that bypasses potential issues
    async def help_trading_wrapper(update, context):
        logger.info(f"help_trading_wrapper called by user {update.effective_user.id if update.effective_user else 'unknown'}")
        
        # Call the original method if it exists
        if handler._original_help_trading:
            try:
                await handler._original_help_trading(update, context)
                return
            except Exception as e:
                logger.error(f"Original help_trading failed: {e}")
        
        # Fallback implementation
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
• **Send Chart Images** - Upload any chart image for AI analysis

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
        
        try:
            await update.message.reply_text(help_message, parse_mode='Markdown')
            logger.info(f"Trading help command processed for user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Error sending trading help message: {str(e)}")
            # Try without markdown
            try:
                await update.message.reply_text(help_message.replace('**', '').replace('`', ''))
            except Exception as e2:
                logger.error(f"Failed to send help even without markdown: {e2}")
    
    # Help alerts wrapper
    async def help_alerts_wrapper(update, context):
        logger.info(f"help_alerts_wrapper called by user {update.effective_user.id if update.effective_user else 'unknown'}")
        
        if handler._original_help_alerts:
            try:
                await handler._original_help_alerts(update, context)
                return
            except Exception as e:
                logger.error(f"Original help_alerts failed: {e}")
        
        help_message = """🚨 **PRICE ALERTS & NOTIFICATIONS**

**⚡ SET PRICE ALERTS:**
• `/alert AAPL above 150` - Alert when Apple goes above $150
• `/alert TSLA below 200` - Alert when Tesla drops below $200
• `/alert NVDA above 500` - Alert when NVIDIA hits $500

**📱 MANAGE YOUR ALERTS:**
• `/alerts` - See all your active alerts
• `/remove_alert 1` - Remove alert #1

**💡 HOW ALERTS WORK:**
• Get notified immediately when price hits
• 24/7 price monitoring
• Simple setup - just stock and target price
• View and remove alerts anytime

🔙 Return to main menu: `/help`"""
        
        try:
            await update.message.reply_text(help_message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(help_message.replace('**', '').replace('`', ''))
    
    # Help advanced wrapper
    async def help_advanced_wrapper(update, context):
        logger.info(f"help_advanced_wrapper called by user {update.effective_user.id if update.effective_user else 'unknown'}")
        
        if handler._original_help_advanced:
            try:
                await handler._original_help_advanced(update, context)
                return
            except Exception as e:
                logger.error(f"Original help_advanced failed: {e}")
        
        help_message = """🧠 **ADVANCED FEATURES FOR PROS**

**🤖 AI PREDICTIONS:**
• `/ai_analysis AAPL` - AI predicts stock movements
• `/signals TSLA` - Get buy/sell signals
• `/deep_analysis NVDA` - Deep dive with AI
• `/advanced SPY` - Advanced S&P 500 analysis

**📈 STRATEGY TESTING:**
• `/backtest AAPL` - Test strategy performance
• `/indicators AAPL` - Technical indicators (RSI, MACD)
• `/risk GOOGL` - Check risk levels

**💡 WHAT THESE DO:**
• AI Analysis - Predicts stock movements
• Backtesting - Test strategies on past data
• Risk Analysis - Shows potential losses
• Indicators - Technical trading signals

🔙 Return to main menu: `/help`"""
        
        try:
            await update.message.reply_text(help_message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(help_message.replace('**', '').replace('`', ''))
    
    # Help examples wrapper
    async def help_examples_wrapper(update, context):
        logger.info(f"help_examples_wrapper called by user {update.effective_user.id if update.effective_user else 'unknown'}")
        
        if handler._original_help_examples:
            try:
                await handler._original_help_examples(update, context)
                return
            except Exception as e:
                logger.error(f"Original help_examples failed: {e}")
        
        help_message = """💡 **USAGE EXAMPLES & TIPS**

**🗣️ NATURAL CONVERSATION:**
• "What's happening with Tesla stock?"
• "Should I buy Apple now?"
• "How's the tech sector performing?"

**📊 COMMAND EXAMPLES:**
• `/price AAPL` → Get Apple's current price
• `/chart TSLA 1d` → Tesla daily chart
• `/analyze NVDA` → AI analysis of NVIDIA
• `/alert SPY above 450` → S&P 500 alert

**🇺🇸 STOCK COVERAGE:**
• Large-cap: AAPL, MSFT, GOOGL, AMZN, TSLA
• ETFs: SPY, QQQ, IWM, VTI, VOO
• Special: BRK.A, BRK.B

**🚀 GETTING STARTED:**
1. Try `/price AAPL` for your first command
2. Ask me a natural question about stocks
3. Set up price alerts for your watchlist

🔙 Back to main help: `/help`"""
        
        try:
            await update.message.reply_text(help_message, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(help_message.replace('**', '').replace('`', ''))
    
    # Replace handlers
    handler.watchlist_command = watchlist_wrapper
    handler.portfolio_command = portfolio_wrapper
    handler.trade_command = trade_wrapper
    handler.trades_command = trades_wrapper
    handler.help_trading_command = help_trading_wrapper
    handler.help_alerts_command = help_alerts_wrapper
    handler.help_advanced_command = help_advanced_wrapper
    handler.help_examples_command = help_examples_wrapper
    
    logger.info("Trading commands patched for fallback services")
    return handler