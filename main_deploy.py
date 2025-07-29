#!/usr/bin/env python3
"""
Lightweight deployment entry point for TradeMaster AI Bot
This version minimizes dependencies and runs with fallback services
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger('TradeMasterDeploy')

async def main():
    """Main entry point for deployment"""
    try:
        logger.info("🚀 TradeMaster AI Bot (Deployment Version) starting...")
        
        # Import and run the main bot with minimal dependencies
        from main import main as bot_main
        await bot_main()
        
    except ImportError as e:
        logger.error(f"Failed to import required module: {e}")
        logger.error("Installing minimal dependencies...")
        
        # Try to run with absolute minimal setup
        try:
            # Import only essential components
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            # Try integrated bot as fallback
            from integrated_bot import main as integrated_main
            await integrated_main()
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}")
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