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
        
        # Get trades from the trade service (where they were stored)
        trades = []
        if hasattr(handler, 'trade_service') and hasattr(handler.trade_service, 'list_trades'):
            # TradeService from deploy folder
            trades = await handler.trade_service.list_trades(user_id)
        elif hasattr(handler, 'portfolio_service') and hasattr(handler.portfolio_service, 'get_trades'):
            # FallbackPortfolioService
            trades = await handler.portfolio_service.get_trades(user_id)
        
        # Build portfolio from trades
        holdings = {}
        for trade in trades:
            symbol = trade['symbol']
            quantity = trade['quantity']
            price = trade['price']
            trade_type = trade.get('type') or trade.get('action', 'unknown')
            
            if symbol not in holdings:
                holdings[symbol] = {'quantity': 0, 'avg_price': 0, 'total_cost': 0}
            
            if trade_type == 'buy':
                # Update average price
                total_cost = holdings[symbol]['total_cost'] + (quantity * price)
                holdings[symbol]['quantity'] += quantity
                if holdings[symbol]['quantity'] > 0:
                    holdings[symbol]['avg_price'] = total_cost / holdings[symbol]['quantity']
                    holdings[symbol]['total_cost'] = total_cost
            else:  # sell
                holdings[symbol]['quantity'] -= quantity
                if holdings[symbol]['quantity'] > 0:
                    holdings[symbol]['total_cost'] = holdings[symbol]['quantity'] * holdings[symbol]['avg_price']
                else:
                    # Remove if quantity is 0 or negative
                    del holdings[symbol]
        
        portfolio = {
            'holdings': holdings,
            'trades': trades
        }
        
        if not portfolio['holdings']:
            response = """💼 **PORTFOLIO DASHBOARD**

*Your portfolio is currently empty.*

Start building your portfolio:
`/trade buy AAPL 10 150`

Available commands:
• `/watchlist` - Manage watchlist
• `/trades` - View trade history
• `/alert` - Set price alerts"""
        else:
            response = "💼 **PORTFOLIO DASHBOARD**\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Calculate portfolio metrics
            total_cost_basis = 0
            total_current_value = 0
            holdings_data = []
            
            # First pass: gather all data
            for symbol, holding in portfolio['holdings'].items():
                quantity = holding['quantity']
                avg_price = holding['avg_price']
                cost_basis = quantity * avg_price
                total_cost_basis += cost_basis
                
                # Try to get current price
                try:
                    price_data = await handler.market_service.get_stock_price(symbol, user_id)
                    current_price = price_data.get('price', avg_price)
                    current_value = quantity * current_price
                    daily_change = price_data.get('change_percent', 0)
                    company_name = price_data.get('company_name', symbol)
                except:
                    current_price = avg_price
                    current_value = cost_basis
                    daily_change = 0
                    company_name = symbol
                
                total_current_value += current_value
                
                holdings_data.append({
                    'symbol': symbol,
                    'company_name': company_name,
                    'quantity': quantity,
                    'avg_price': avg_price,
                    'current_price': current_price,
                    'cost_basis': cost_basis,
                    'current_value': current_value,
                    'daily_change': daily_change,
                    'unrealized_pnl': current_value - cost_basis,
                    'unrealized_pnl_pct': ((current_value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
                })
            
            # Portfolio Summary
            total_pnl = total_current_value - total_cost_basis
            total_pnl_pct = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
            
            response += "**📈 PORTFOLIO SUMMARY**\n"
            response += f"• Total Value: ${total_current_value:,.2f}\n"
            response += f"• Cost Basis: ${total_cost_basis:,.2f}\n"
            response += f"• Total P&L: ${total_pnl:+,.2f} ({total_pnl_pct:+.2f}%)\n"
            response += f"• Holdings: {len(holdings_data)} positions\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Holdings Details
            response += "**💎 HOLDINGS BREAKDOWN**\n\n"
            
            # Sort by current value (largest positions first)
            holdings_data.sort(key=lambda x: x['current_value'], reverse=True)
            
            for holding in holdings_data:
                # Calculate allocation percentage
                allocation = (holding['current_value'] / total_current_value * 100) if total_current_value > 0 else 0
                
                # Position header
                response += f"**{holding['symbol']}** - {holding['company_name'][:20]}\n"
                response += f"├ Position: {holding['quantity']} shares @ ${holding['avg_price']:.2f}\n"
                response += f"├ Current: ${holding['current_price']:.2f} ({holding['daily_change']:+.2f}% today)\n"
                response += f"├ Value: ${holding['current_value']:,.2f} ({allocation:.1f}% of portfolio)\n"
                response += f"└ P&L: ${holding['unrealized_pnl']:+,.2f} ({holding['unrealized_pnl_pct']:+.2f}%)\n\n"
            
            # Performance Metrics
            response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            response += "**📊 PERFORMANCE METRICS**\n\n"
            
            # Calculate detailed performance metrics
            winners = [h for h in holdings_data if h['unrealized_pnl'] > 0]
            losers = [h for h in holdings_data if h['unrealized_pnl'] < 0]
            flat = [h for h in holdings_data if h['unrealized_pnl'] == 0]
            
            # Win/Loss Statistics
            total_positions = len(holdings_data)
            win_rate = (len(winners) / total_positions * 100) if total_positions > 0 else 0
            
            response += "**Win/Loss Analysis:**\n"
            response += f"• Win Rate: {win_rate:.1f}%\n"
            response += f"• Winners: {len(winners)} | Losers: {len(losers)} | Flat: {len(flat)}\n"
            
            # Calculate average gains and losses
            if winners:
                avg_win_pct = sum(w['unrealized_pnl_pct'] for w in winners) / len(winners)
                avg_win_dollar = sum(w['unrealized_pnl'] for w in winners) / len(winners)
                response += f"• Avg Winner: +${avg_win_dollar:,.2f} (+{avg_win_pct:.2f}%)\n"
            
            if losers:
                avg_loss_pct = sum(l['unrealized_pnl_pct'] for l in losers) / len(losers)
                avg_loss_dollar = sum(l['unrealized_pnl'] for l in losers) / len(losers)
                response += f"• Avg Loser: ${avg_loss_dollar:,.2f} ({avg_loss_pct:.2f}%)\n"
            
            # Risk/Reward Ratio
            if winners and losers:
                avg_win_pct = sum(w['unrealized_pnl_pct'] for w in winners) / len(winners)
                avg_loss_pct = abs(sum(l['unrealized_pnl_pct'] for l in losers) / len(losers))
                risk_reward = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else float('inf')
                response += f"• Risk/Reward Ratio: {risk_reward:.2f}:1\n"
            
            response += "\n**Position Performance:**\n"
            
            # Best and worst performers with more detail
            if holdings_data:
                sorted_by_pnl = sorted(holdings_data, key=lambda x: x['unrealized_pnl_pct'], reverse=True)
                
                # Top 3 performers (or all if less than 3)
                top_count = min(3, len(sorted_by_pnl))
                if top_count > 0:
                    response += "• Top Performers:\n"
                    for i in range(top_count):
                        h = sorted_by_pnl[i]
                        if h['unrealized_pnl'] >= 0:
                            response += f"  {i+1}. {h['symbol']}: +${h['unrealized_pnl']:,.2f} ({h['unrealized_pnl_pct']:+.2f}%)\n"
                
                # Bottom 3 performers (if any losers)
                bottom_performers = [h for h in sorted_by_pnl if h['unrealized_pnl'] < 0]
                if bottom_performers:
                    response += "• Bottom Performers:\n"
                    for i, h in enumerate(bottom_performers[-3:]):
                        response += f"  {i+1}. {h['symbol']}: ${h['unrealized_pnl']:,.2f} ({h['unrealized_pnl_pct']:.2f}%)\n"
            
            # Portfolio Concentration Risk
            response += "\n**Risk Analysis:**\n"
            if holdings_data:
                # Find largest position by value
                largest = max(holdings_data, key=lambda x: x['current_value'])
                concentration = (largest['current_value'] / total_current_value * 100)
                response += f"• Largest Position: {largest['symbol']} ({concentration:.1f}% of portfolio)\n"
                
                # Calculate portfolio volatility approximation
                pnl_percentages = [h['unrealized_pnl_pct'] for h in holdings_data]
                if len(pnl_percentages) > 1:
                    import statistics
                    try:
                        volatility = statistics.stdev(pnl_percentages)
                        response += f"• Position Volatility: {volatility:.2f}%\n"
                    except:
                        pass
            
            # Recent Activity
            if portfolio['trades']:
                response += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                response += "**🕐 RECENT ACTIVITY**\n"
                for trade in portfolio['trades'][-5:][::-1]:  # Last 5 trades, newest first
                    trade_type = trade.get('type') or trade.get('action', 'unknown')
                    trade_emoji = '🟢' if trade_type == 'buy' else '🔴'
                    
                    # Format timestamp
                    timestamp_field = trade.get('timestamp') or trade.get('executed_at', '')
                    if isinstance(timestamp_field, str) and 'T' in timestamp_field:
                        date_part = timestamp_field.split('T')[0]
                    else:
                        date_part = str(timestamp_field).split(' ')[0]
                    
                    response += f"{trade_emoji} {date_part}: {trade_type.upper()} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}\n"
        
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
        
        # Use trade service if available (matches /trade command)
        if hasattr(handler, 'trade_service') and hasattr(handler.trade_service, 'list_trades'):
            # TradeService from deploy folder
            trades = await handler.trade_service.list_trades(user_id)
        elif hasattr(handler, 'portfolio_service') and hasattr(handler.portfolio_service, 'get_trades'):
            # FallbackPortfolioService
            trades = await handler.portfolio_service.get_trades(user_id)
        else:
            # Create fallback service
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
            response = "📊 **TRADE EXECUTION HISTORY**\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Calculate summary statistics
            total_volume = 0
            buy_count = 0
            sell_count = 0
            symbols_traded = set()
            
            for trade in trades:
                trade_type = trade.get('type') or trade.get('action', 'unknown')
                total_volume += trade['quantity'] * trade['price']
                symbols_traded.add(trade['symbol'])
                if trade_type == 'buy':
                    buy_count += 1
                else:
                    sell_count += 1
            
            # Summary section
            response += f"**📈 SUMMARY STATISTICS**\n"
            response += f"• Total Trades: {len(trades)}\n"
            response += f"• Buy Orders: {buy_count} | Sell Orders: {sell_count}\n"
            response += f"• Total Volume: ${total_volume:,.2f}\n"
            response += f"• Unique Symbols: {len(symbols_traded)}\n"
            response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            # Detailed trades section
            response += "**📋 RECENT EXECUTIONS**\n\n"
            
            # Show last 15 trades with enhanced formatting
            for i, trade in enumerate(trades[-15:][::-1], 1):  # Reverse to show newest first
                # Handle different field names between services
                trade_type = trade.get('type') or trade.get('action', 'unknown')
                trade_emoji = '🟢' if trade_type == 'buy' else '🔴'
                
                # Handle different timestamp field names
                timestamp_field = trade.get('timestamp') or trade.get('executed_at', '')
                if isinstance(timestamp_field, str):
                    # Parse ISO format to readable format
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp_field.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        date_str = timestamp_field.split('T')[0]
                        time_str = timestamp_field.split('T')[1][:8] if 'T' in timestamp_field else ''
                else:
                    # Handle datetime objects
                    date_str = str(timestamp_field).split(' ')[0]
                    time_str = str(timestamp_field).split(' ')[1].split('.')[0] if ' ' in str(timestamp_field) else ''
                
                # Calculate total if not present
                total = trade.get('total', trade['quantity'] * trade['price'])
                
                # Format trade entry with better structure
                response += f"{trade_emoji} **Trade #{trade['id']}**\n"
                response += f"   📅 {date_str}"
                if time_str:
                    response += f" at {time_str}"
                response += f"\n"
                response += f"   📊 {trade_type.upper()}: {trade['quantity']} × {trade['symbol']} @ ${trade['price']:.2f}\n"
                response += f"   💵 Total Value: ${total:,.2f}\n"
                
                # Add separator between trades except last one
                if i < min(15, len(trades)):
                    response += "   ─────────────────────\n"
            
            response += f"\n_Showing {min(15, len(trades))} most recent trades out of {len(trades)} total_"
        
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