#!/usr/bin/env python3
"""
Simplified TradeMaster AI Bot without security features
"""
import os
import sys
import asyncio
import logging
from aiohttp import web

# Add deploy directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deploy'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TradeMasterAI')

# Import the simplified telegram handler
from simplified_telegram_handler import SimplifiedTelegramHandler

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "TradeMaster AI Bot",
        "version": "2.0"
    })

async def main():
    """Main application entry point"""
    try:
        # Create web app for health checks
        app = web.Application()
        app.router.add_get('/', health_handler)
        app.router.add_get('/health', health_handler)
        
        # Start web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        logger.info("✅ Health server started on port 5000")
        
        # Create and run the simplified handler
        handler = SimplifiedTelegramHandler()
        logger.info("✅ TradeMaster AI Bot starting (simplified version)...")
        
        # Run the bot
        await handler.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())