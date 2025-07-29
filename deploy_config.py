#!/usr/bin/env python3
"""
Deployment configuration for TradeAI Telegram Bot
Simplified version for production deployment
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DeployConfig')

class DeploymentConfig:
    """Simplified deployment configuration"""
    
    def __init__(self):
        self.telegram_token = os.getenv('TELEGRAM_API_TOKEN', '')
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.port = int(os.getenv('PORT', 8080))
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
    def validate(self) -> bool:
        """Validate essential configuration"""
        if not self.telegram_token:
            logger.error("TELEGRAM_API_TOKEN is required")
            return False
            
        if not self.openai_key:
            logger.error("OPENAI_API_KEY is required")
            return False
            
        logger.info("Configuration validation successful")
        return True
    
    def get_config_summary(self) -> dict:
        """Get configuration summary for logging"""
        return {
            'telegram_configured': bool(self.telegram_token),
            'openai_configured': bool(self.openai_key),
            'port': self.port,
            'debug_mode': self.debug
        }

# Global config instance
config = DeploymentConfig()