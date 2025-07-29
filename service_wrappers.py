"""
Service wrappers to provide fallback functionality when dependencies are missing
"""
import logging
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger('ServiceWrappers')

class FallbackMarketDataService:
    """Fallback market data service when yfinance is not available"""
    
    def __init__(self):
        logger.info("Using fallback market data service")
        self.demo_stocks = {
            'AAPL': {'name': 'Apple Inc.', 'price': 185.50, 'sector': 'Technology'},
            'MSFT': {'name': 'Microsoft Corporation', 'price': 425.00, 'sector': 'Technology'},
            'GOOGL': {'name': 'Alphabet Inc.', 'price': 142.75, 'sector': 'Technology'},
            'AMZN': {'name': 'Amazon.com Inc.', 'price': 178.25, 'sector': 'Consumer Cyclical'},
            'TSLA': {'name': 'Tesla Inc.', 'price': 252.50, 'sector': 'Automotive'},
            'META': {'name': 'Meta Platforms Inc.', 'price': 512.00, 'sector': 'Technology'},
            'NVDA': {'name': 'NVIDIA Corporation', 'price': 825.75, 'sector': 'Technology'},
            'BRK.B': {'name': 'Berkshire Hathaway Inc.', 'price': 415.00, 'sector': 'Financial'},
            'JPM': {'name': 'JPMorgan Chase & Co.', 'price': 198.50, 'sector': 'Financial'},
            'V': {'name': 'Visa Inc.', 'price': 275.25, 'sector': 'Financial Services'},
        }
    
    async def get_stock_price(self, symbol: str, user_id: Optional[int] = None) -> Dict:
        """Get simulated stock price"""
        symbol = symbol.upper()
        
        # Check if it's a known stock
        if symbol in self.demo_stocks:
            stock = self.demo_stocks[symbol]
            base_price = stock['price']
            
            # Add some random variation
            change_percent = random.uniform(-3, 3)
            change = base_price * (change_percent / 100)
            current_price = base_price + change
            
            return {
                'symbol': symbol,
                'company_name': stock['name'],
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': random.randint(10000000, 50000000),
                'day_low': current_price * 0.98,
                'day_high': current_price * 1.02,
                'low_52w': base_price * 0.7,
                'high_52w': base_price * 1.3,
                'market_cap': f'{int(base_price * random.uniform(100, 2000))}B',
                'pe_ratio': round(random.uniform(15, 35), 2),
                'source': 'Demo Data (Real-time data requires API configuration)'
            }
        else:
            # For unknown stocks, return a generic response
            base_price = random.uniform(10, 500)
            change_percent = random.uniform(-3, 3)
            change = base_price * (change_percent / 100)
            
            return {
                'symbol': symbol,
                'company_name': f'{symbol} Corporation',
                'price': base_price,
                'change': change,
                'change_percent': change_percent,
                'volume': random.randint(1000000, 10000000),
                'day_low': base_price * 0.98,
                'day_high': base_price * 1.02,
                'source': 'Demo Data (Real-time data requires API configuration)'
            }
    
    async def get_market_summary(self) -> Dict:
        """Get simulated market summary"""
        indices = {
            'S&P 500': {'value': 5000 + random.uniform(-50, 50), 'change': random.uniform(-1, 1)},
            'NASDAQ': {'value': 15000 + random.uniform(-150, 150), 'change': random.uniform(-1.5, 1.5)},
            'DOW': {'value': 40000 + random.uniform(-200, 200), 'change': random.uniform(-0.8, 0.8)},
            'FTSE': {'value': 7500 + random.uniform(-50, 50), 'change': random.uniform(-0.5, 0.5)},
            'NIKKEI': {'value': 35000 + random.uniform(-300, 300), 'change': random.uniform(-1, 1)},
            'DAX': {'value': 18000 + random.uniform(-100, 100), 'change': random.uniform(-0.7, 0.7)}
        }
        
        formatted_indices = {}
        for name, data in indices.items():
            change_sign = '+' if data['change'] >= 0 else ''
            formatted_indices[name] = f"{data['value']:,.2f} ({change_sign}{data['change']:.2f}%)"
        
        return {
            'indices': formatted_indices,
            'sentiment': 'Mixed' if random.random() > 0.5 else 'Bullish',
            'source': 'Demo Data'
        }
    
    async def get_trending_stocks(self) -> List[Dict]:
        """Get trending stocks"""
        stocks = list(self.demo_stocks.keys())
        random.shuffle(stocks)
        trending = stocks[:5]
        
        return [
            {
                'symbol': symbol,
                'name': self.demo_stocks[symbol]['name'],
                'price': self.demo_stocks[symbol]['price'],
                'change_percent': random.uniform(-5, 5)
            }
            for symbol in trending
        ]

class FallbackWatchlistService:
    """Fallback watchlist service for user portfolios"""
    
    def __init__(self):
        self.watchlists = {}
        logger.info("Using fallback watchlist service")
    
    async def get_user_watchlist(self, user_id: int) -> List[str]:
        """Get user's watchlist"""
        return self.watchlists.get(str(user_id), [])
    
    async def add_to_watchlist(self, user_id: int, symbol: str) -> bool:
        """Add symbol to watchlist"""
        user_id_str = str(user_id)
        if user_id_str not in self.watchlists:
            self.watchlists[user_id_str] = []
        
        if symbol not in self.watchlists[user_id_str]:
            self.watchlists[user_id_str].append(symbol)
            return True
        return False
    
    async def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """Remove symbol from watchlist"""
        user_id_str = str(user_id)
        if user_id_str in self.watchlists and symbol in self.watchlists[user_id_str]:
            self.watchlists[user_id_str].remove(symbol)
            return True
        return False

class FallbackPortfolioService:
    """Fallback portfolio tracking service"""
    
    def __init__(self):
        self.portfolios = {}
        self.trade_counter = 1
        logger.info("Using fallback portfolio service")
    
    async def record_trade(self, user_id: int, trade_type: str, symbol: str, quantity: float, price: float) -> Dict:
        """Record a trade"""
        user_id_str = str(user_id)
        if user_id_str not in self.portfolios:
            self.portfolios[user_id_str] = {'trades': [], 'holdings': {}}
        
        trade = {
            'id': self.trade_counter,
            'type': trade_type,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': quantity * price,
            'timestamp': datetime.now().isoformat()
        }
        
        self.portfolios[user_id_str]['trades'].append(trade)
        self.trade_counter += 1
        
        # Update holdings
        holdings = self.portfolios[user_id_str]['holdings']
        if symbol not in holdings:
            holdings[symbol] = {'quantity': 0, 'avg_price': 0}
        
        if trade_type == 'buy':
            total_cost = holdings[symbol]['quantity'] * holdings[symbol]['avg_price'] + quantity * price
            holdings[symbol]['quantity'] += quantity
            holdings[symbol]['avg_price'] = total_cost / holdings[symbol]['quantity'] if holdings[symbol]['quantity'] > 0 else 0
        else:  # sell
            holdings[symbol]['quantity'] -= quantity
            if holdings[symbol]['quantity'] <= 0:
                del holdings[symbol]
        
        return {'success': True, 'trade_id': trade['id']}
    
    async def get_portfolio(self, user_id: int) -> Dict:
        """Get user's portfolio"""
        user_id_str = str(user_id)
        if user_id_str not in self.portfolios:
            return {'holdings': {}, 'trades': [], 'total_value': 0}
        
        portfolio = self.portfolios[user_id_str]
        total_value = sum(h['quantity'] * h['avg_price'] for h in portfolio['holdings'].values())
        
        return {
            'holdings': portfolio['holdings'],
            'trades': portfolio['trades'][-10:],  # Last 10 trades
            'total_value': total_value
        }
    
    async def get_trades(self, user_id: int) -> List[Dict]:
        """Get user's trade history"""
        user_id_str = str(user_id)
        if user_id_str not in self.portfolios:
            return []
        return self.portfolios[user_id_str]['trades']

class FallbackChartService:
    """Fallback chart service"""
    
    def __init__(self):
        logger.info("Using fallback chart service")
    
    async def generate_price_chart(self, symbol: str, period: str = '1mo') -> Optional[str]:
        """Return a placeholder message for charts"""
        return None  # Will trigger text-based response instead
    
    async def analyze_chart_image(self, image_data: bytes) -> str:
        """Analyze chart image"""
        return (
            "Chart analysis is currently unavailable. "
            "To enable chart analysis, please configure the required dependencies. "
            "I can still help you with price data and market information using text-based commands."
        )

def inject_fallback_services(handler):
    """Inject fallback services into the telegram handler"""
    try:
        # Check if real services are working
        if hasattr(handler, 'market_service'):
            # Test if yfinance is available
            try:
                import yfinance
            except ImportError:
                logger.info("Injecting fallback market data service")
                handler.market_service = FallbackMarketDataService()
        
        # Add watchlist service if missing
        if not hasattr(handler, 'watchlist_service'):
            logger.info("Injecting fallback watchlist service")
            handler.watchlist_service = FallbackWatchlistService()
        
        # Add portfolio service if missing
        if not hasattr(handler, 'portfolio_service'):
            logger.info("Injecting fallback portfolio service")
            handler.portfolio_service = FallbackPortfolioService()
        
        # Replace chart service if matplotlib is missing
        if hasattr(handler, 'chart_service'):
            try:
                import matplotlib
            except ImportError:
                logger.info("Injecting fallback chart service")
                handler.chart_service = FallbackChartService()
        
        logger.info("Fallback services injection completed")
        return handler
    
    except Exception as e:
        logger.error(f"Error injecting fallback services: {e}")
        return handler