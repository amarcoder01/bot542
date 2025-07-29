#!/usr/bin/env python3
"""
TradeMaster AI Bot - Main Entry Point
Integrates TelegramHandler with health server on port 5000
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from aiohttp import web

# Add deploy directory to Python path for imports
deploy_dir = Path(__file__).parent / 'deploy'
if deploy_dir.exists():
    sys.path.insert(0, str(deploy_dir))
else:
    print("Error: deploy directory not found")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TradeMasterAI')

# Health server for monitoring
async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'bot': 'TradeMaster AI',
        'version': '2.0'
    })

async def main():
    """Main entry point that runs TelegramHandler with health server"""
    try:
        # Import TelegramHandler from deploy folder
        from telegram_handler import TelegramHandler
        
        logger.info("=== Starting TradeMaster AI Bot ===")
        logger.info("Using full telegram_handler.py from deploy folder")
        
        # Create health server
        health_app = web.Application()
        health_app.router.add_get('/health', health_check)
        health_app.router.add_get('/', health_check)
        
        # Start health server
        runner = web.AppRunner(health_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 5000)
        await site.start()
        logger.info("✅ Health server started on port 5000")
        
        # Create and run the handler
        handler = TelegramHandler()
        
        # Inject fallback services for missing dependencies
        from service_wrappers import inject_fallback_services
        handler = inject_fallback_services(handler)
        
        # Add missing services that aren't in the original handler
        from service_wrappers import FallbackWatchlistService, FallbackPortfolioService
        if not hasattr(handler, 'watchlist_service'):
            handler.watchlist_service = FallbackWatchlistService()
        if not hasattr(handler, 'portfolio_service'):
            handler.portfolio_service = FallbackPortfolioService()
        if not hasattr(handler, 'trade_service'):
            handler.trade_service = handler.portfolio_service  # Use portfolio service for trades
        
        # Patch trading commands to work with fallback services
        from command_patches import patch_trading_commands
        handler = patch_trading_commands(handler)
        
        logger.info("✅ TradeMaster AI Bot starting with fallback services...")
        
        # Run the bot in a task
        bot_task = asyncio.create_task(handler.run())
        
        # Keep running
        try:
            await bot_task
        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            # Cleanup
            logger.info("Shutting down bot...")
            if hasattr(handler, 'stop'):
                await handler.stop()
            await runner.cleanup()
            logger.info("Bot shutdown complete")
    
    except ImportError as e:
        logger.error(f"Failed to import TelegramHandler: {e}")
        logger.error("Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    # Check for required environment variable
    if not os.getenv('TELEGRAM_API_TOKEN'):
        logger.error("TELEGRAM_API_TOKEN environment variable is required")
        sys.exit(1)
    
    # Run the bot
    asyncio.run(main())