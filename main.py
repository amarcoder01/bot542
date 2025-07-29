#!/usr/bin/env python3
"""
Production-ready main entry point for TradeAI Telegram Bot
Configured for deployment with proper error handling and monitoring
"""
import os
import sys
import asyncio
import logging
import signal
import time
from typing import Optional
from pathlib import Path

# Add deploy directory to Python path for imports
deploy_dir = Path(__file__).parent / 'deploy'
sys.path.insert(0, str(deploy_dir))

# Also add current directory
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TradeAI')

# Import deployment config
from deploy_config import config

class TelegramBotDeployment:
    """Production deployment class for Telegram bot"""
    
    def __init__(self):
        self.telegram_handler = None
        self.web_app = None
        self.start_time = time.time()
        self.is_ready = False
        logger.info("🤖 TradeAI Telegram Bot initializing...")
    
    def validate_environment(self) -> bool:
        """Validate required environment variables using deployment config"""
        if not config.validate():
            logger.error("❌ Environment validation failed")
            logger.error("Please check your TELEGRAM_API_TOKEN and OPENAI_API_KEY")
            return False
        
        logger.info("✅ Environment validation successful")
        logger.info(f"Configuration: {config.get_config_summary()}")
        return True
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            logger.info("🛑 Received shutdown signal, stopping bot...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Cleanup resources on shutdown"""
        try:
            if self.telegram_handler:
                logger.info("Stopping Telegram handler...")
                # Add cleanup logic here
            if self.web_app:
                logger.info("Stopping web server...")
                # Add web app cleanup here
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def start_health_server(self):
        """Start health check server for monitoring"""
        try:
            from aiohttp import web
            
            async def health_check(request):
                uptime = int(time.time() - self.start_time)
                return web.json_response({
                    'status': 'healthy' if self.is_ready else 'starting',
                    'uptime_seconds': uptime,
                    'version': '1.0.0',
                    'service': 'TradeAI Telegram Bot'
                })
            
            async def root_handler(request):
                return web.Response(
                    text="TradeAI Telegram Bot is running! 🤖", 
                    status=200,
                    headers={'Content-Type': 'text/plain'}
                )
            
            app = web.Application()
            app.router.add_get('/', root_handler)
            app.router.add_get('/health', health_check)
            app.router.add_get('/ready', health_check)
            
            port = int(os.environ.get('PORT', 8080))
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            self.web_app = runner
            logger.info(f"🌐 Health server running on port {port}")
            
        except Exception as e:
            logger.error(f"Failed to start health server: {e}")
            raise
    
    async def initialize_bot(self):
        """Initialize the Telegram bot with all services"""
        try:
            # Import bot components from deploy directory
            from telegram_handler import TelegramHandler
            from config import Config
            
            # Initialize configuration
            config = Config()
            
            # Create and initialize Telegram handler
            self.telegram_handler = TelegramHandler()
            
            # Start the bot
            await self.telegram_handler.start()
            
            self.is_ready = True
            logger.info("✅ Telegram bot initialized and ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise
    
    async def run(self):
        """Main run method for the bot"""
        try:
            # Validate environment
            if not self.validate_environment():
                return
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Start health server
            await self.start_health_server()
            
            # Initialize and start bot
            await self.initialize_bot()
            
            logger.info("🚀 TradeAI Telegram Bot is fully operational!")
            logger.info("📊 Bot features:")
            logger.info("  • Real-time market data")
            logger.info("  • AI-powered analysis")
            logger.info("  • Price alerts")
            logger.info("  • Portfolio tracking")
            logger.info("  • Technical indicators")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                if not self.is_ready:
                    logger.warning("Bot not ready, attempting restart...")
                    await self.initialize_bot()
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Critical error in bot: {e}")
            raise
        finally:
            self.cleanup()

async def main():
    """Main entry point"""
    try:
        bot = TelegramBotDeployment()
        await bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())